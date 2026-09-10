[CmdletBinding()]
param(
    [switch]$AppOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$appRoot = Join-Path $repoRoot "app"
$python = Join-Path $appRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Die lokale Python-Umgebung fehlt: $python"
}

$resultsDir = Join-Path $repoRoot "output\test-results"
New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null
$resultFile = Join-Path $resultsDir ("pytest-{0}.xml" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
$testArgs = @("-m", "pytest", "-q", "--reuse-db", "--junitxml", $resultFile)
if ($AppOnly) {
    $testArgs += "tests"
}

Push-Location $appRoot
try {
    & $python @testArgs
    $exitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

if (-not (Test-Path -LiteralPath $resultFile)) {
    throw "Pytest hat keinen auswertbaren Ergebnisbericht geschrieben."
}
[xml]$result = Get-Content -Raw -LiteralPath $resultFile
$suite = @($result.testsuites.testsuite | Select-Object -First 1)
$summary = $suite | Select-Object tests, failures, errors, skipped, time
Write-Host "JUnit-Ergebnis: $resultFile"
$summary | Format-List | Out-Host

if ($exitCode -ne 0) {
    throw "Pytest ist mit Exit-Code $exitCode fehlgeschlagen."
}
