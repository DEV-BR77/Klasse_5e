[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$container = "klasse-5e-klasse-5e-app-1"
$running = docker inspect --format "{{.State.Running}}" $container 2>$null
if ($LASTEXITCODE -ne 0 -or $running -ne "true") {
    throw "The Klasse 5e application container is not running."
}
docker exec $container python manage.py sync_webuntis --automatic
if ($LASTEXITCODE -ne 0) {
    throw "WebUntis synchronization failed with exit code $LASTEXITCODE."
}
