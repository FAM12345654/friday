param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$LogDirectory = Join-Path $Root "local_data\logs"
$ResultPath = Join-Path $LogDirectory "friday-api-stale-cleanup.json"
New-Item -ItemType Directory -Force -Path $LogDirectory | Out-Null

$stopped = [System.Collections.Generic.List[int]]::new()
$blocked = [System.Collections.Generic.List[object]]::new()
$listeners = @(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)

foreach ($listener in $listeners) {
    $processId = [int]$listener.OwningProcess
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$processId" -ErrorAction SilentlyContinue
    $commandLine = [string]$process.CommandLine
    $name = [string]$process.Name
    $isFridayUvicorn = (
        $name -match "(?i)^python(?:\.exe)?$" -and
        $commandLine -match "(?i)(?:^|\s)-m\s+uvicorn(?:\s|$)" -and
        $commandLine -match "(?i)(?:^|\s)main:app(?:\s|$)" -and
        $commandLine -match "(?i)(?:^|\s)--port\s+$Port(?:\s|$)"
    )
    if (-not $isFridayUvicorn) {
        $blocked.Add([ordered]@{
            pid = $processId
            name = $name
            reason = "listener_not_verified_as_friday_uvicorn"
        })
        continue
    }
    Stop-Process -Id $processId -Force -ErrorAction Stop
    $stopped.Add($processId)
}

$result = [ordered]@{
    timestamp = (Get-Date).ToString("o")
    port = $Port
    stopped = @($stopped)
    blocked = @($blocked)
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ResultPath -Encoding UTF8
if ($blocked.Count -gt 0) {
    exit 2
}
