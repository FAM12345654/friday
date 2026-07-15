param(
    [int]$Port = 8001,
    [string]$TokenPath = "",
    [int]$MaxRestarts = 3,
    [int]$RestartDelaySeconds = 60
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$ApiDirectory = Join-Path $Root "friday-api"
$LogDirectory = Join-Path $Root "local_data\logs"
$PidPath = Join-Path $LogDirectory "friday-api-autostart.pid"
$HealthUrl = "http://127.0.0.1:$Port/health"
$ContractUrl = "http://127.0.0.1:$Port/openapi.json"
$RequiredContractPath = "/api/calendar/source-sync/preview-status"
if ([string]::IsNullOrWhiteSpace($TokenPath)) {
    $TokenPath = Join-Path $Root "local_data\secrets\friday-api-token.txt"
}

function Get-PythonExecutable {
    $knownPython = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
    if (Test-Path -LiteralPath $knownPython) {
        return $knownPython
    }

    $command = Get-Command python.exe -ErrorAction Stop
    return $command.Source
}

function Import-FridayApiToken {
    $token = [string]$env:FRIDAY_API_TOKEN
    if ([string]::IsNullOrWhiteSpace($token)) {
        $token = [string][Environment]::GetEnvironmentVariable("FRIDAY_API_TOKEN", "User")
    }
    if ([string]::IsNullOrWhiteSpace($token) -and (Test-Path -LiteralPath $TokenPath)) {
        $token = Get-Content -LiteralPath $TokenPath -Raw
    }
    $token = $token.Trim()
    if ($token.Length -lt 32) {
        throw "Friday API Token fehlt oder ist kürzer als 32 Zeichen."
    }
    $env:FRIDAY_API_TOKEN = $token
}

function Test-FridayHealth {
    try {
        $response = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 3 -ErrorAction Stop
        return $response.ok -eq $true
    }
    catch {
        return $false
    }
}

function Test-FridayContract {
    try {
        $headers = @{ Authorization = "Bearer $env:FRIDAY_API_TOKEN" }
        $contract = Invoke-RestMethod -Uri $ContractUrl -Headers $headers -TimeoutSec 5 -ErrorAction Stop
        return $null -ne $contract.paths.PSObject.Properties[$RequiredContractPath]
    }
    catch {
        return $false
    }
}

Import-FridayApiToken

$listeners = @(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
if ($listeners.Count -gt 0) {
    $unsafeListeners = @(
        $listeners | Where-Object { $_.LocalAddress -notin @("127.0.0.1", "::1") }
    )
    if ($unsafeListeners.Count -gt 0) {
        throw "Port $Port ist bereits außerhalb von Loopback gebunden. Friday startet aus Sicherheitsgründen nicht."
    }
    if ((Test-FridayHealth) -and (Test-FridayContract)) {
        exit 0
    }
    throw "Port $Port ist belegt, aber Friday Health-/Vertragscheck ist fehlgeschlagen."
}

New-Item -ItemType Directory -Force -Path $LogDirectory | Out-Null
$python = Get-PythonExecutable
$safeMaxRestarts = [Math]::Max(0, [Math]::Min($MaxRestarts, 10))
$safeRestartDelay = [Math]::Max(1, [Math]::Min($RestartDelaySeconds, 300))
$lastFailure = "Friday API wurde unerwartet beendet."

for ($restartAttempt = 0; $restartAttempt -le $safeMaxRestarts; $restartAttempt++) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $suffix = if ($restartAttempt -gt 0) { "-restart$restartAttempt" } else { "" }
    $stdoutPath = Join-Path $LogDirectory "api-autostart-$stamp$suffix.out.log"
    $stderrPath = Join-Path $LogDirectory "api-autostart-$stamp$suffix.err.log"
    $startArguments = @{
        FilePath = $python
        ArgumentList = (
            "-m uvicorn main:app --app-dir `"$ApiDirectory`" " +
            "--host 127.0.0.1 --port $Port"
        )
        WorkingDirectory = $Root
        WindowStyle = "Hidden"
        RedirectStandardOutput = $stdoutPath
        RedirectStandardError = $stderrPath
        PassThru = $true
    }
    $process = Start-Process @startArguments
    Set-Content -LiteralPath $PidPath -Value $process.Id -Encoding ASCII

    $ready = $false
    for ($readinessAttempt = 0; $readinessAttempt -lt 60; $readinessAttempt++) {
        if ($process.HasExited) { break }
        if ((Test-FridayHealth) -and (Test-FridayContract)) {
            $ready = $true
            break
        }
        Start-Sleep -Milliseconds 500
    }

    if ($ready) {
        $process.WaitForExit()
        $process.Refresh()
        $lastFailure = "Friday API wurde unerwartet mit Exit-Code $($process.ExitCode) beendet."
    }
    else {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        $lastFailure = "Friday API wurde nicht mit aktuellem Vertrag bereit. Siehe $stderrPath"
    }

    if ($restartAttempt -lt $safeMaxRestarts) {
        Start-Sleep -Seconds $safeRestartDelay
    }
}

throw $lastFailure
