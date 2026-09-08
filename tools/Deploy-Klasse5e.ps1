[CmdletBinding()]
param([switch]$NoBuild)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$secretTool = "C:\Users\Bjoern\.homeops\tools\Get-HomeOpsSecret.ps1"
$secretMap = [ordered]@{
    RESEND_API_KEY = "providers/resend/klassid_api_key"
    POSTGRES_PASSWORD = "projects/klasse-5e/postgres_password"
    DJANGO_SECRET_KEY = "projects/klasse-5e/django_secret_key"
    VISION_SERVICE_TOKEN = "projects/klasse-5e/vision_service_token"
    WEBUNTIS_CREDENTIAL_ENCRYPTION_KEY = "klasse-5e/webuntis/credential-encryption-key"
    ITSLEARNING_CREDENTIAL_ENCRYPTION_KEY = "projects/klasse-5e/itslearning_credential_encryption_key"
    VAPID_PUBLIC_KEY = "projects/klasse-5e/vapid_public_key"
    VAPID_PRIVATE_KEY = "projects/klasse-5e/vapid_private_key"
    SPOONACULAR_API_KEY = "klasse5e/spoonacular-api-key"
    MOBILITY_DATA_ENCRYPTION_KEY = "projects/klasse-5e/mobility_data_encryption_key"
}

$previous = @{}
try {
    foreach ($name in $secretMap.Keys) {
        $previous[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
        $secure = & $secretTool -Name $secretMap[$name]
        $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
        try {
            [Environment]::SetEnvironmentVariable(
                $name,
                [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer),
                "Process"
            )
        }
        finally {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
        }
    }
    $runningContainer = (& docker compose ps -q klasse-5e-app).Trim()
    if ($runningContainer) {
        $runningImage = (& docker inspect --format '{{.Image}}' $runningContainer).Trim()
        $rollbackTag = "klasse-5e-app:rollback-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        & docker image tag $runningImage $rollbackTag
        if ($LASTEXITCODE -ne 0) {
            throw "Could not create rollback tag for the running app image."
        }
        Write-Host "Rollback image retained as $rollbackTag"
    }

    if (-not $NoBuild) {
        # Build and load only the application image.  Building all services made
        # Compose recreate Vision as a side effect, which can interrupt a healthy
        # rollout after the app image was already exported.
        & docker compose build --progress plain klasse-5e-app
        if ($LASTEXITCODE -ne 0) {
            throw "Application image build failed with exit code $LASTEXITCODE."
        }
    }

    & docker image inspect klasse-5e-app:0.3.0b4 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "The application image was not loaded after the build."
    }

    # Do not restart PostgreSQL or Vision.  --force-recreate is necessary when
    # the release image keeps the same tag as the preceding build.
    & docker compose up -d --no-deps --no-build --force-recreate klasse-5e-app
    if ($LASTEXITCODE -ne 0) {
        throw "Application rollout failed with exit code $LASTEXITCODE."
    }

    $deployedContainer = (& docker compose ps -q klasse-5e-app).Trim()
    if (-not $deployedContainer) {
        throw "Compose did not create the application container."
    }
    $health = "starting"
    for ($attempt = 1; $attempt -le 45; $attempt++) {
        $health = (& docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' $deployedContainer).Trim()
        if ($health -eq "healthy") {
            break
        }
        if ($health -eq "unhealthy" -or $health -eq "exited") {
            break
        }
        Start-Sleep -Seconds 2
    }
    if ($health -ne "healthy") {
        throw "Application container is not healthy after rollout (state: $health)."
    }
    & docker compose ps klasse-5e-app klasse-5e-db klasse-5e-vision
}
finally {
    foreach ($name in $secretMap.Keys) {
        [Environment]::SetEnvironmentVariable($name, $previous[$name], "Process")
    }
}
