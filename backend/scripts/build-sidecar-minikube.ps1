param(
    [string]$ImageTag = "aicodereviewer-sidecar:latest",
    [string]$ProjectId = "",
    [switch]$ForceBuild
)

$ErrorActionPreference = "Stop"

$backendRoot = Split-Path -Parent $PSScriptRoot
$sidecarRoot = Join-Path $backendRoot "sidecar"
$flattenedKubeconfig = Join-Path $backendRoot ".kube\config.flattened"

if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) {
    throw "minikube bulunamadi. Once minikube kur veya PATH'e ekle."
}

if (-not (Test-Path $sidecarRoot)) {
    throw "Sidecar dizini bulunamadi: $sidecarRoot"
}

$existingImages = minikube image ls
$imageExists = $false
if ($existingImages) {
    $needle = [Regex]::Escape($ImageTag)
    $imageExists = $existingImages | Where-Object { $_ -match "(^|/)$needle$" } | Select-Object -First 1
}

if ($imageExists -and -not $ForceBuild) {
    Write-Host "Image zaten mevcut, build atlandi: $ImageTag"
    Write-Host "Zorla build icin -ForceBuild kullan."
}
else {
    Write-Host "Sidecar image build basliyor: $ImageTag"
    minikube image build -t $ImageTag $sidecarRoot
}

if ($ProjectId) {
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        throw "kubectl bulunamadi. rollout restart icin kubectl gerekli."
    }

    if (Test-Path $flattenedKubeconfig) {
        $env:KUBECONFIG = $flattenedKubeconfig
    }

    $namespace = "project-$ProjectId"
    $deployment = "project-$ProjectId"

    Write-Host "Deployment restart: $deployment (ns: $namespace)"
    kubectl rollout restart "deployment/$deployment" -n $namespace
    kubectl rollout status "deployment/$deployment" -n $namespace --timeout=180s
}
