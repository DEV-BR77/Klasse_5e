[CmdletBinding()]
param([switch]$NoBuild)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$secretTool = "C:\Users\Bjoern\.homeops\tools\Get-HomeOpsSecret.ps1"
$secretMap = [ordered]@{
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
    $arguments = @("compose", "up", "-d")
    if (-not $NoBuild) {
        $arguments += "--build"
    }
    & docker @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Docker deployment failed with exit code $LASTEXITCODE."
    }
    & docker compose ps
}
finally {
    foreach ($name in $secretMap.Keys) {
        [Environment]::SetEnvironmentVariable($name, $previous[$name], "Process")
    }
}
