param(
    [int]$Port = 8000,
    [Alias("Host")]
    [string]$BindHost = "127.0.0.1",
    [switch]$SkipKubeconfigRefresh
)

$ErrorActionPreference = "Stop"

$backendRoot = Split-Path -Parent $PSScriptRoot
$kubeDir = Join-Path $backendRoot ".kube"
$flattenedKubeconfig = Join-Path $kubeDir "config.flattened"

if (-not $SkipKubeconfigRefresh) {
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        throw "kubectl bulunamadi. Once kubectl kur veya PATH'e ekle."
    }

    if (-not (Test-Path $kubeDir)) {
        New-Item -ItemType Directory -Path $kubeDir | Out-Null
    }

    kubectl config view --raw --flatten | Set-Content -LiteralPath $flattenedKubeconfig
    Write-Host "Kubeconfig guncellendi: $flattenedKubeconfig"
}

if (-not (Test-Path $flattenedKubeconfig)) {
    throw "Kubeconfig bulunamadi: $flattenedKubeconfig (SkipKubeconfigRefresh kullanma ya da dosyayi olustur)."
}

$env:KUBECONFIG = $flattenedKubeconfig
if (-not $env:DEBUG) {
    $env:DEBUG = "true"
}

Write-Host "Backend baslatiliyor..."
Write-Host "KUBECONFIG=$env:KUBECONFIG"
Write-Host "DEBUG=$env:DEBUG"
Write-Host "URL=http://$BindHost`:$Port"

Push-Location $backendRoot
try {
    python -m uvicorn main:app --host $BindHost --port $Port
}
finally {
    Pop-Location
}
