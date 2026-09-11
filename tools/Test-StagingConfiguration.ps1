[CmdletBinding()]
param(
    [string]$EnvironmentFile = "staging.public.env"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$environmentPath = Join-Path $repoRoot $EnvironmentFile
if (-not (Test-Path -LiteralPath $environmentPath)) {
    throw "Staging-Konfiguration fehlt: $environmentPath. Verwende staging.public.env und die verschlüsselt gespeicherten Staging-Schlüssel."
}

$composeFiles = @(
    (Join-Path $repoRoot "compose.yaml"),
    (Join-Path $repoRoot "compose.staging.yaml")
)
foreach ($composeFile in $composeFiles) {
    if (-not (Test-Path -LiteralPath $composeFile)) {
        throw "Compose-Datei fehlt: $composeFile"
    }
}

$composeArgs = @("compose", "--env-file", $environmentPath)
foreach ($composeFile in $composeFiles) {
    $composeArgs += @("-f", $composeFile)
}
$composeArgs += @("config", "--format", "json")
$config = & docker @composeArgs
if ($LASTEXITCODE -ne 0) {
    throw "Docker Compose konnte die Staging-Konfiguration nicht validieren."
}

$resolved = $config | ConvertFrom-Json
if ($resolved.name -ne "klasse-5e-staging") {
    throw "Das Compose-Projekt muss klasse-5e-staging heißen."
}
$app = $resolved.services."klasse-5e-app"
$environment = @{}
foreach ($property in $app.environment.PSObject.Properties) {
    $environment[$property.Name] = [string]$property.Value
}

foreach ($key in @("DJANGO_ALLOWED_HOSTS", "DJANGO_CSRF_TRUSTED_ORIGINS", "APP_BASE_URL")) {
    if ([string]::IsNullOrWhiteSpace($environment[$key])) {
        throw "Die Staging-Variable $key fehlt."
    }
    if ($environment[$key] -match '(^|,)\s*(https://)?klassid\.de(?=[:/,]|$)') {
        throw "Die Staging-Variable $key darf nicht auf das Produktivportal zeigen."
    }
}
if ($environment["TEMPORARY_ADMIN_MFA_BYPASS"] -ne "0") {
    throw "MFA-Bypass ist in Staging verboten."
}
if ($environment["BIOMETRIC_SEARCH_ENABLED"] -ne "0") {
    throw "Biometrische Suche ist in Staging standardmäßig deaktiviert."
}

$expectedVolumes = @{
    "postgres_data" = "klasse-5e-staging-postgres-data"
    "app_media" = "klasse-5e-staging-app-media"
    "vision_data" = "klasse-5e-staging-vision-data"
    "vision_models" = "klasse-5e-staging-vision-models"
}
foreach ($volumeName in $expectedVolumes.Keys) {
    $actualName = $resolved.volumes.$volumeName.name
    if ($actualName -ne $expectedVolumes[$volumeName]) {
        throw "Das Volume $volumeName ist nicht von der Produktivumgebung getrennt."
    }
}

Write-Host "Staging-Compose-Konfiguration ist getrennt und gültig. Es wurden keine Container gestartet."
