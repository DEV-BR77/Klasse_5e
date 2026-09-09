[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$modelRevision = "96cb0d0342c7afb80cab76ecc58b265fa44da256"
$expectedSha256 = "1ec2fbe9fd8551fbcce260d8a10d3e012d8818bfeac046d7e2dba5a8aa7c7b55"
$volumeName = "klasse-5e-vision-models"
$modelPath = "/models/falconsai-nsfw-96cb0d0/model.onnx"
$exporterImage = "klassid-nsfw-export:temp"

function Read-InstalledChecksum {
    $result = docker run --rm --entrypoint sha256sum `
        -v "${volumeName}:/models:ro" `
        klasse-5e-vision:0.1.0 $modelPath 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $result) {
        return ""
    }
    return ($result -split "\s+")[0].ToLowerInvariant()
}

if ((Read-InstalledChecksum) -eq $expectedSha256) {
    Write-Output "Das gepinnte Chat-Sicherheitsmodell ist bereits geprüft installiert."
    exit 0
}

$dockerfile = Join-Path $env:TEMP "klassid-nsfw-export.Dockerfile"
try {
    @"
FROM python:3.12-slim-bookworm
RUN python -m pip install --no-cache-dir "torch==2.7.1" --index-url https://download.pytorch.org/whl/cpu
RUN python -m pip install --no-cache-dir "optimum[onnxruntime]==1.27.0" "transformers==4.52.4" "huggingface_hub==0.36.0"
"@ | Set-Content -LiteralPath $dockerfile -Encoding utf8

    docker build -f $dockerfile -t $exporterImage $env:TEMP
    if ($LASTEXITCODE -ne 0) { throw "Exporter-Image konnte nicht gebaut werden." }

    $command = @"
rm -rf /models/falconsai-nsfw-96cb0d0 /tmp/source &&
python -c 'from huggingface_hub import snapshot_download; snapshot_download(repo_id="Falconsai/nsfw_image_detection", revision="$modelRevision", local_dir="/tmp/source", allow_patterns=["config.json","preprocessor_config.json","model.safetensors"])' &&
optimum-cli export onnx --model /tmp/source --task image-classification /models/falconsai-nsfw-96cb0d0
"@
    docker run --rm -v "${volumeName}:/models" $exporterImage sh -lc $command
    if ($LASTEXITCODE -ne 0) { throw "Das Modell konnte nicht exportiert werden." }

    $actualSha256 = Read-InstalledChecksum
    if ($actualSha256 -ne $expectedSha256) {
        throw "Die exportierte Modelldatei stimmt nicht mit der freigegebenen Prüfsumme überein."
    }
    Write-Output "Das Chat-Sicherheitsmodell wurde geprüft installiert."
}
finally {
    Remove-Item -LiteralPath $dockerfile -Force -ErrorAction SilentlyContinue
}
