param(
  [string]$Channel = "preview",
  [switch]$NoPublish,
  [switch]$BuildAndroid,
  [switch]$NoPause
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Root) {
  $Root = (Get-Location).Path
}

$MobileDir = Join-Path $Root "friday-mobile"
$ToolsDir = Join-Path $Root "tools"
$LogsDir = Join-Path $Root "logs"
$Cloudflared = Join-Path $ToolsDir "cloudflared.exe"
$EnvPath = Join-Path $MobileDir ".env"
$AppJsonPath = Join-Path $MobileDir "app.json"
$ClientPath = Join-Path $MobileDir "src\api\client.js"
$LiveSummaryPath = Join-Path $LogsDir "friday-mobile-live.txt"
$TunnelOutLog = Join-Path $LogsDir "cloudflared.out.log"
$TunnelErrLog = Join-Path $LogsDir "cloudflared.err.log"
$TunnelPidPath = Join-Path $LogsDir "cloudflared.pid"

function Write-Step($Message) {
  Write-Host ""
  Write-Host "== $Message"
}

function Set-KeyValueFile($Path, $Key, $Value) {
  $lines = @()
  if (Test-Path $Path) {
    $lines = Get-Content $Path
  }

  $found = $false
  $updated = foreach ($line in $lines) {
    if ($line -match "^$([regex]::Escape($Key))=") {
      $found = $true
      "$Key=$Value"
    } else {
      $line
    }
  }

  if (-not $found) {
    $updated += "$Key=$Value"
  }

  Set-Content -Path $Path -Value $updated -Encoding ASCII
}

function Update-MobileApiUrl($Url) {
  Set-KeyValueFile -Path $EnvPath -Key "EXPO_PUBLIC_FRIDAY_API_URL" -Value $Url

  $appJson = Get-Content $AppJsonPath -Raw
  $appJson = $appJson -replace '"fridayApiDefaultUrl"\s*:\s*"[^"]+"', ('"fridayApiDefaultUrl": "' + $Url + '"')
  Set-Content -Path $AppJsonPath -Value $appJson -Encoding ASCII

  $client = Get-Content $ClientPath -Raw
  $client = $client -replace '"https://[^"]+\.trycloudflare\.com"', ('"' + $Url + '"')
  Set-Content -Path $ClientPath -Value $client -Encoding ASCII
}

function Get-TunnelUrlFromLogs {
  $text = ""
  if (Test-Path $TunnelOutLog) {
    $text += Get-Content $TunnelOutLog -Raw -ErrorAction SilentlyContinue
  }
  if (Test-Path $TunnelErrLog) {
    $text += "`n" + (Get-Content $TunnelErrLog -Raw -ErrorAction SilentlyContinue)
  }

  $match = [regex]::Match($text, "https://[a-zA-Z0-9-]+\.trycloudflare\.com")
  if ($match.Success) {
    return $match.Value
  }

  return $null
}

function Wait-ForUrl($Url, $Path) {
  $target = "$Url$Path"
  for ($i = 0; $i -lt 120; $i++) {
    try {
      $response = Invoke-WebRequest -Uri $target -UseBasicParsing -TimeoutSec 5
      if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
        return $true
      }
    } catch {
      Start-Sleep -Seconds 1
    }
  }
  return $false
}

function Start-QuickTunnel {
  if (Test-Path $TunnelPidPath) {
    $oldPid = Get-Content $TunnelPidPath -ErrorAction SilentlyContinue
    if ($oldPid) {
      Stop-Process -Id $oldPid -Force -ErrorAction SilentlyContinue
    }
  }

  Remove-Item $TunnelOutLog, $TunnelErrLog -Force -ErrorAction SilentlyContinue
  $process = Start-Process -FilePath $Cloudflared -ArgumentList @("tunnel", "--url", "http://127.0.0.1:8000", "--no-autoupdate") -RedirectStandardOutput $TunnelOutLog -RedirectStandardError $TunnelErrLog -WindowStyle Hidden -PassThru
  Set-Content -Path $TunnelPidPath -Value $process.Id -Encoding ASCII

  $url = $null
  for ($i = 0; $i -lt 60; $i++) {
    Start-Sleep -Seconds 1
    $url = Get-TunnelUrlFromLogs
    if ($url) {
      break
    }
  }

  if (-not $url) {
    throw "Keine Cloudflare-Tunnel-URL gefunden. Siehe $TunnelErrLog"
  }

  return @{
    Process = $process
    Url = $url
  }
}

Write-Step "Friday Mobile live schalten"
New-Item -ItemType Directory -Force -Path $ToolsDir, $LogsDir | Out-Null

if (-not (Test-Path $Cloudflared)) {
  Write-Step "Cloudflare Tunnel Client herunterladen"
  Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile $Cloudflared
}

Write-Step "Friday API lokal starten oder wiederverwenden"
try {
  Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 3 | Out-Null
  Write-Host "API läuft bereits auf 127.0.0.1:8000"
} catch {
  Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "cd /d `"$Root`" && start_friday_api.bat" -WindowStyle Hidden | Out-Null
  Start-Sleep -Seconds 8
}

Write-Step "Remote HTTPS-Tunnel starten"
$tunnelInfo = $null
$remoteUrl = $null
$healthOk = $false
$dashboardOk = $false

for ($attempt = 1; $attempt -le 3; $attempt++) {
  Write-Host "Tunnel-Versuch $attempt/3"
  $tunnelInfo = Start-QuickTunnel
  $tunnel = $tunnelInfo.Process
  $remoteUrl = $tunnelInfo.Url
  Write-Host "Remote API Kandidat: $remoteUrl"

  Write-Step "Remote API vom Handy-Weg simulieren"
  $healthOk = Wait-ForUrl -Url $remoteUrl -Path "/health"
  $dashboardOk = Wait-ForUrl -Url $remoteUrl -Path "/api/dashboard"
  if ($healthOk -and $dashboardOk) {
    break
  }

  Write-Host "Tunnel noch nicht erreichbar, starte neu..."
}

if (-not $healthOk -or -not $dashboardOk) {
  throw "Remote API ist nach mehreren Tunnel-Versuchen nicht sauber erreichbar."
}

Write-Host "Remote API OK"

Write-Step "Mobile-App auf Remote API setzen"
Update-MobileApiUrl -Url $remoteUrl

$updateUrl = ""
if (-not $NoPublish) {
  Write-Step "EAS Update auf Channel '$Channel' veröffentlichen"
  Push-Location $MobileDir
  try {
    $updateOutput = npx eas-cli@latest update --channel $Channel --message "Friday live API $remoteUrl" 2>&1
    $updateOutput | Tee-Object -FilePath (Join-Path $LogsDir "eas-update-$Channel.log")
    $match = [regex]::Match(($updateOutput | Out-String), "https://expo\.dev/accounts/[^\s]+")
    if ($match.Success) {
      $updateUrl = $match.Value
    }
  } finally {
    Pop-Location
  }
}

$buildUrl = ""
if ($BuildAndroid) {
  Write-Step "Android APK Build starten"
  Push-Location $MobileDir
  try {
    $buildOutput = npx eas-cli@latest build --platform android --profile preview --non-interactive --no-wait 2>&1
    $buildOutput | Tee-Object -FilePath (Join-Path $LogsDir "eas-android-build-start.log")
    $match = [regex]::Match(($buildOutput | Out-String), "https://expo\.dev/accounts/[^\s]+")
    if ($match.Success) {
      $buildUrl = $match.Value
    }
  } finally {
    Pop-Location
  }
}

$summary = @(
  "Friday Mobile LIVE",
  "Zeit: $(Get-Date -Format s)",
  "Remote API: $remoteUrl",
  "Channel: $Channel",
  "EAS Update: $updateUrl",
  "Android Build: $buildUrl",
  "Tunnel PID: $($tunnel.Id)",
  "",
  "Handy-Hinweis:",
  "1. Installierte Friday-App komplett schließen.",
  "2. Wieder öffnen.",
  "3. Falls kein Update erscheint, App noch einmal schließen und öffnen."
)

Set-Content -Path $LiveSummaryPath -Value $summary -Encoding UTF8

Write-Step "Fertig"
$summary | ForEach-Object { Write-Host $_ }

if (-not $NoPause) {
  Write-Host ""
  Read-Host "Enter zum Schließen"
}
