[CmdletBinding()]
param(
    [string]$BackupRoot = "D:\Backups\Klasse5e-Files"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# This is a source/configuration backup only.  It deliberately excludes
# secrets, tests, build output and Docker runtime data.  PostgreSQL and the
# named Docker media volumes need their own backup procedure.
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$snapshotRoot = Join-Path $BackupRoot "Klasse5e-Files-$timestamp"

if ([IO.Path]::GetFullPath($BackupRoot).TrimEnd("\\") -like "$repoRoot*") {
    throw "Das Backup-Ziel darf nicht innerhalb des Klasse-5e-Repositories liegen."
}

New-Item -ItemType Directory -Force -Path $snapshotRoot | Out-Null

function Invoke-Robocopy {
    param(
        [Parameter(Mandatory)] [string]$Source,
        [Parameter(Mandatory)] [string]$Destination,
        [string[]]$Files = @("*"),
        [string[]]$ExcludeDirectories = @(),
        [string[]]$ExcludeFiles = @()
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Die zu sichernde Quelle fehlt: $Source"
    }
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null

    $arguments = @($Source, $Destination) + $Files + @(
        "/E", "/COPY:DAT", "/DCOPY:DAT", "/R:2", "/W:2", "/XJ", "/FFT", "/NP", "/NFL", "/NDL"
    )
    if ($ExcludeDirectories.Count) { $arguments += "/XD"; $arguments += $ExcludeDirectories }
    if ($ExcludeFiles.Count) { $arguments += "/XF"; $arguments += $ExcludeFiles }

    & robocopy @arguments
    if ($LASTEXITCODE -gt 7) {
        throw "Robocopy konnte '$Source' nicht sichern (Exit-Code $LASTEXITCODE)."
    }
}

# Produktiver Django-/PWA-Quellstand und die dafür benötigten Docker-Dateien.
$directories = @(
    "app\src",
    "app\templates",
    "app\static",
    "app\theme",
    "app\docker",
    "avatar",
    "packages\web-push-kit",
    "services",
    "docs"
)
foreach ($relativePath in $directories) {
    Invoke-Robocopy -Source (Join-Path $repoRoot $relativePath) -Destination (Join-Path $snapshotRoot $relativePath) `
        -ExcludeDirectories @(".venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", "tests", "test", "staticfiles", "runtime-media", ".test-media", ".test-runtime") `
        -ExcludeFiles @("~$*", "*.pyc", "*.pyo", "*.sqlite3")
}

# Einzeldateien, die zum Bauen und Betreiben der Anwendung gehören.
$rootFiles = @(
    "AGENTS.md",
    "PROJECT.md",
    "README.md",
    "compose.yaml",
    "compose.staging.yaml",
    "compose.dev.yaml",
    ".dockerignore",
    ".env.docker.example",
    ".env.staging.example",
    "schools.csv"
)
foreach ($file in $rootFiles) {
    $sourceFile = Join-Path $repoRoot $file
    if (Test-Path -LiteralPath $sourceFile) {
        Invoke-Robocopy -Source $repoRoot -Destination $snapshotRoot -Files @($file)
    }
}

# Die produktive Reverse-Proxy-Route liegt bewusst im Infrastrukturprojekt.
$caddyRoute = "D:\Development\Repos\HomeInfrastructure\caddy\managed\klasse-5e.caddy"
if (Test-Path -LiteralPath $caddyRoute) {
    Invoke-Robocopy -Source (Split-Path $caddyRoute) -Destination (Join-Path $snapshotRoot "infrastructure\caddy\managed") -Files @("klasse-5e.caddy")
}

$manifest = @"
KlassID-Dateisicherung: $timestamp

Enthalten:
- Django-Quellcode, Templates, statische Dateien, Theme und Avatar-Assets
- Docker-/Compose-Konfiguration, Web-Push-Kit, Services und Projektdokumentation
- produktive KlassID-Caddy-Route

Bewusst nicht enthalten:
- .env-Dateien, API-Schluessel und andere Geheimnisse
- Tests, virtuelle Umgebungen, Caches, generierte staticfiles und Build-Ausgaben
- PostgreSQL-Datenbank und Docker-Volumes (insbesondere Medien)
"@
Set-Content -LiteralPath (Join-Path $snapshotRoot "BACKUP-INHALT.txt") -Value $manifest -Encoding utf8

Write-Host "Dateisicherung erstellt: $snapshotRoot"
Write-Host "Hinweis: Datenbank und Docker-Volumes sind absichtlich nicht enthalten."
