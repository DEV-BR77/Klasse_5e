[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$runner = Join-Path $PSScriptRoot "Invoke-Klasse5eWebUntisSync.ps1"
if (-not (Test-Path -LiteralPath $runner)) {
    throw "Synchronization runner was not found."
}
$escapedRunner = '"' + $runner + '"'
foreach ($time in @("06:00", "12:00", "18:00")) {
    $suffix = $time.Replace(":", "")
    $taskName = "Klasse5e-WebUntis-$suffix"
    $command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File $escapedRunner"
    schtasks.exe /Create /F /SC DAILY /ST $time /TN $taskName /TR $command | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Could not register scheduled task $taskName."
    }
    Write-Output "Registered $taskName."
}
