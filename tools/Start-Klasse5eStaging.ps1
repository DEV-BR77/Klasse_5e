[CmdletBinding(SupportsShouldProcess)]
param(
    [switch]$Start
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$configFile = Join-Path $repoRoot 'staging.public.env'
$secretReader = Join-Path $env:USERPROFILE '.homeops\tools\Get-HomeOpsSecret.ps1'

if (-not (Test-Path -LiteralPath $configFile)) {
    throw "Nicht geheime Staging-Konfiguration fehlt: $configFile"
}
if (-not (Test-Path -LiteralPath $secretReader)) {
    throw "HomeOps-Secret-Werkzeug fehlt: $secretReader"
}

$secretNames = [ordered]@{
    POSTGRES_PASSWORD = 'projects/klasse-5e-staging/postgres_password'
    DJANGO_SECRET_KEY = 'projects/klasse-5e-staging/django_secret_key'
    VISION_SERVICE_TOKEN = 'projects/klasse-5e-staging/vision_service_token'
    WEBUNTIS_CREDENTIAL_ENCRYPTION_KEY = 'projects/klasse-5e-staging/webuntis_credential_encryption_key'
    ITSLEARNING_CREDENTIAL_ENCRYPTION_KEY = 'projects/klasse-5e-staging/itslearning_credential_encryption_key'
    MOBILITY_DATA_ENCRYPTION_KEY = 'projects/klasse-5e-staging/mobility_data_encryption_key'
    VAPID_PUBLIC_KEY = 'projects/klasse-5e-staging/vapid_public_key'
    VAPID_PRIVATE_KEY = 'projects/klasse-5e-staging/vapid_private_key'
    RESEND_API_KEY = 'providers/resend/klassid_staging_api_key'
    MONITORING_INGEST_TOKEN = 'projects/klasse-5e-staging/monitoring_ingest_token'
}

$injectedNames = New-Object System.Collections.Generic.List[string]
try {
    foreach ($entry in $secretNames.GetEnumerator()) {
        $value = & $secretReader -Name $entry.Value -AsPlainText
        if ([string]::IsNullOrWhiteSpace($value)) {
            throw "Das erforderliche Staging-Secret '$($entry.Value)' ist leer."
        }
        Set-Item -LiteralPath "Env:$($entry.Key)" -Value $value
        $injectedNames.Add($entry.Key)
    }

    $composeArgs = @(
        'compose', '--env-file', $configFile,
        '-f', (Join-Path $repoRoot 'compose.yaml'),
        '-f', (Join-Path $repoRoot 'compose.staging.yaml')
    )
    & (Join-Path $PSScriptRoot 'Test-StagingConfiguration.ps1') -EnvironmentFile 'staging.public.env'
    if ($LASTEXITCODE -ne 0) {
        throw 'Die Staging-Konfiguration ist ungültig.'
    }
    if (-not $Start) {
        Write-Host 'Staging-Konfiguration geprüft. Mit -Start werden die getrennten Container gebaut und gestartet.'
        return
    }
    if ($PSCmdlet.ShouldProcess('klasse-5e-staging', 'Container bauen und starten')) {
        & docker @composeArgs up -d --build
        if ($LASTEXITCODE -ne 0) {
            throw 'Docker Compose konnte Staging nicht starten.'
        }
        Write-Host 'Staging-Container wurden mit separaten Volumes gestartet.'
    }
}
finally {
    foreach ($name in $injectedNames) {
        Remove-Item -LiteralPath "Env:$name" -ErrorAction SilentlyContinue
    }
}
