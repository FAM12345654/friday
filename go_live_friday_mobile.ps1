param(
  [string]$Channel = "preview",
  [switch]$NoPublish,
  [switch]$BuildAndroid,
  [switch]$NoPause
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Root) { $Root = (Get-Location).Path }
$MobileDir = Join-Path $Root "friday-mobile"
$LogsDir = Join-Path $Root "local_data\logs"
$LiveSummaryPath = Join-Path $LogsDir "friday-mobile-live.txt"
$RemoteUrl = "https://pc.tail4c6152.ts.net"
$configuredPort = [string]$env:FRIDAY_API_PORT
if ([string]::IsNullOrWhiteSpace($configuredPort)) {
  $configuredPort = [string][Environment]::GetEnvironmentVariable("FRIDAY_API_PORT", "User")
}
$ApiPort = if ($configuredPort) { [int]$configuredPort } else { 8001 }

function Write-Step([string]$Message) {
  Write-Host ""
  Write-Host "== $Message"
}

function Get-FridayApiToken {
  $token = [string]$env:FRIDAY_API_TOKEN
  if ([string]::IsNullOrWhiteSpace($token)) {
    $token = [string][Environment]::GetEnvironmentVariable("FRIDAY_API_TOKEN", "User")
  }
  $token = $token.Trim()
  if ($token.Length -lt 32) {
    throw "FRIDAY_API_TOKEN fehlt oder ist kürzer als 32 Zeichen."
  }
  return $token
}

function Wait-FridayEndpoint([string]$Url, [hashtable]$Headers = @{}) {
  for ($attempt = 0; $attempt -lt 60; $attempt++) {
    try {
      $response = Invoke-RestMethod -Uri $Url -Headers $Headers -TimeoutSec 5 -ErrorAction Stop
      if ($response.ok -eq $true) { return $response }
    }
    catch { Start-Sleep -Seconds 1 }
  }
  throw "Friday-Endpunkt wurde nicht rechtzeitig erreichbar: $Url"
}

New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
$ApiToken = Get-FridayApiToken
$ApiHeaders = @{ Authorization = "Bearer $ApiToken" }

Write-Step "Friday API über den kontrollierten Autostart bereitstellen"
Start-ScheduledTask -TaskName "Friday API Autostart"
Wait-FridayEndpoint -Url "http://127.0.0.1:$ApiPort/health" | Out-Null
Wait-FridayEndpoint -Url "http://127.0.0.1:$ApiPort/api/setup/status" -Headers $ApiHeaders | Out-Null

Write-Step "Stabiles Tailscale HTTPS Serve konfigurieren"
tailscale serve reset | Out-Null
tailscale serve --bg --https=443 --yes "http://127.0.0.1:$ApiPort" | Out-Null
Wait-FridayEndpoint -Url "$RemoteUrl/health" | Out-Null
Wait-FridayEndpoint -Url "$RemoteUrl/api/setup/status" -Headers $ApiHeaders | Out-Null

Write-Step "Release-Vertrag prüfen"
& (Join-Path $Root "verify_friday_mobile_release.ps1")
if ($LASTEXITCODE -ne 0) { throw "Mobile Release-Verifikation ist fehlgeschlagen." }

$buildUrl = ""
if ($BuildAndroid) {
  Write-Step "Neuen nativen Android-Preview-Build starten"
  Push-Location $MobileDir
  try {
    $buildOutput = npx eas-cli@latest build --platform android --profile preview --non-interactive --no-wait 2>&1
    $buildOutput | Tee-Object -FilePath (Join-Path $LogsDir "eas-android-build-start.log")
    $match = [regex]::Match(($buildOutput | Out-String), "https://expo\.dev/accounts/[^\s]+")
    if ($match.Success) { $buildUrl = $match.Value }
  }
  finally { Pop-Location }
}

$updateUrl = ""
if (-not $NoPublish) {
  Write-Step "EAS Update auf die getrennte Secure-v2-Runtime veröffentlichen"
  Push-Location $MobileDir
  try {
    $updateOutput = npx eas-cli@latest update --channel $Channel --message "Friday stable Tailscale HTTPS" --non-interactive 2>&1
    $updateOutput | Tee-Object -FilePath (Join-Path $LogsDir "eas-update-$Channel.log")
    $match = [regex]::Match(($updateOutput | Out-String), "https://expo\.dev/accounts/[^\s]+")
    if ($match.Success) { $updateUrl = $match.Value }
  }
  finally { Pop-Location }
}

$summary = @(
  "Friday Mobile LIVE",
  "Zeit: $(Get-Date -Format s)",
  "Remote API: $RemoteUrl",
  "API-Port lokal: $ApiPort (Loopback)",
  "Channel: $Channel",
  "EAS Update: $updateUrl",
  "Android Build: $buildUrl",
  "",
  "Handy-Hinweis:",
  "1. Neuen Secure-v2-APK-Build installieren.",
  "2. Unter Datenschutz denselben API-Token im Geräte-Keystore speichern.",
  "3. Dashboard, Posteingang, Kalender, Voice und Neustart prüfen."
)
$summary | Set-Content -LiteralPath $LiveSummaryPath -Encoding UTF8
$summary | ForEach-Object { Write-Host $_ }

if (-not $NoPause) { Read-Host "Enter zum Schließen" | Out-Null }
