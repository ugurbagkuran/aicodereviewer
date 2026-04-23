param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [string]$Path = "/files?path=/"
)

$ErrorActionPreference = "Stop"

$hostHeader = "project-$ProjectId.localhost"
$url = "http://127.0.0.1$Path"

Write-Host "Host: $hostHeader"
Write-Host "URL : $url"

curl.exe -i -H "Host: $hostHeader" $url
