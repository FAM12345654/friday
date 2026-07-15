param(
    [switch]$SummaryOnly,
    [switch]$AsJson
)

try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
    $OutputEncoding = [Console]::OutputEncoding
}
catch {
    # Keep verification running even on older shells with limited encoding support.
}

$showDetails = -not $SummaryOnly

$apiHost = $env:FRIDAY_API_HOST
if ([string]::IsNullOrWhiteSpace($apiHost)) {
    $apiHost = "127.0.0.1"
}

$apiPort = $env:FRIDAY_API_PORT
if ([string]::IsNullOrWhiteSpace($apiPort)) {
    $apiPort = "8000"
}

$projectRoot = $PSScriptRoot
$mobileDir = Join-Path $projectRoot "friday-mobile"
$desktopDir = Join-Path $projectRoot "friday-desktop"
$mobileEnvPath = Join-Path $mobileDir ".env"

$baseUrl = "http://${apiHost}:${apiPort}"
$apiToken = [string]$env:FRIDAY_API_TOKEN
$apiHeaders = @{}
if (-not [string]::IsNullOrWhiteSpace($apiToken)) {
    $apiHeaders.Authorization = "Bearer $($apiToken.Trim())"
}
$endpoints = @(
    "/health",
    "/api/dashboard",
    "/api/tasks",
    "/api/messages",
    "/api/calendar",
    "/api/contacts",
    "/api/privacy"
)

$failed = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()
$recommendations = [System.Collections.Generic.List[string]]::new()
$checkResults = [System.Collections.Generic.List[string]]::new()
$checkCounts = @{ OK = 0; WARN = 0; FAIL = 0 }

function Add-CheckResult {
    param(
        [ValidateSet("OK", "WARN", "FAIL")]
        [string]$Status,
        [string]$Message
    )

    $checkResults.Add("[$Status] $Message")
    $checkCounts[$Status]++
}

function Parse-EnvValue {
    param(
        [string]$Line
    )

    $trimmed = $Line.Trim()
    if (-not $trimmed.Contains("=")) {
        return @{ Key = $null; Value = $null }
    }

    if ($trimmed.StartsWith("#")) {
        return @{ Key = $null; Value = $null }
    }

    $parts = $trimmed -split "=", 2
    return @{ Key = $parts[0].Trim(); Value = $parts[1].Trim().Trim('"') }
}

function Add-WarningIfMissingPath {
    param(
        [string]$PathToCheck,
        [string]$MessageIfMissing
    )

    if (-not (Test-Path $PathToCheck)) {
        $warnings.Add($MessageIfMissing)
        Add-CheckResult -Status "WARN" -Message $MessageIfMissing
    }
    else {
        Add-CheckResult -Status "OK" -Message "Found required path: $PathToCheck"
    }
}

function Add-Failure {
    param(
        [string]$Failure,
        [string]$Recommendation
    )

    $failed.Add($Failure)
    if ($Recommendation) {
        $recommendations.Add($Recommendation)
    }
}

function Get-EndpunktFailureRecommendation {
    param(
        [string]$Endpoint,
        [Exception]$Error
    )

    $message = $Error.Message
    $innerMessage = ""
    if ($Error.InnerException) {
        $innerMessage = $Error.InnerException.Message
    }

    $combined = "$message $innerMessage".ToLower()

    if ($combined -match "connection refused|actively refused") {
        return "API-Dienst auf $baseUrl scheint nicht zu laufen. Starte ihn über start_friday_api.bat und prüfe, ob Port $apiPort belegt ist."
    }
    if ($combined -match "timed out|timeout") {
        return "Zeitüberschreitung beim Zugriff auf $endpoint. Prüfe Host/Port und lokale Firewall/Proxy-Einstellungen."
    }
    if ($combined -match "name resolution|could not resolve host|no such host|dns") {
        return "DNS/Hostname ungültig. Überprüfe EXPO_PUBLIC_FRIDAY_API_URL und FRIDAY_API_HOST (127.0.0.1, 10.0.2.2 oder LAN-IP)."
    }
    if ($combined -match "404") {
        return "Der API-Pfad existiert nicht oder Routing ist falsch. Prüfe, dass der FastAPI-Server mit uvicorn main:app läuft."
    }

    return "Starte die API erneut (start_friday_api.bat) und prüfe Netzwerkzugriff auf $baseUrl."
}

function Write-OutputLine {
    param(
        [string]$Text,
        [ConsoleColor]$ForegroundColor = [ConsoleColor]::White,
        [switch]$Always
    )

    if (-not $SummaryOnly -or $Always.IsPresent) {
        Write-Host $Text -ForegroundColor $ForegroundColor
    }
}

function Write-SummaryJson {
    param(
        [string]$Status
    )

    if (-not $AsJson) {
        return
    }

    $payload = [ordered]@{
        status      = $Status
        baseUrl     = $baseUrl
        checks      = [ordered]@{
            ok   = $checkCounts["OK"]
            warn = $checkCounts["WARN"]
            fail = $checkCounts["FAIL"]
        }
        failed      = $failed
        warnings    = $warnings
        checksTable = $checkResults
        recommendations = $recommendations | Sort-Object -Unique
    }

    Write-Output ""
    $payload | ConvertTo-Json -Depth 6
}

Write-OutputLine "Friday service check (API)" -ForegroundColor Cyan -Always
Write-OutputLine "API base URL: $baseUrl" -Always

$isLoopbackApiHost = $apiHost -in @("127.0.0.1", "localhost", "::1")
if (-not [string]::IsNullOrWhiteSpace($apiToken) -and $apiToken.Trim().Length -lt 32) {
    Add-Failure "FRIDAY_API_TOKEN ist kürzer als 32 Zeichen." "Erzeuge einen neuen zufälligen Token mit mindestens 32 Zeichen."
    Add-CheckResult -Status "FAIL" -Message "FRIDAY_API_TOKEN is too short."
}
elseif (-not $isLoopbackApiHost -and [string]::IsNullOrWhiteSpace($apiToken)) {
    Add-Failure "Netzwerk-Host '$apiHost' ist ohne FRIDAY_API_TOKEN konfiguriert." "Setze einen starken Token oder binde die API an 127.0.0.1."
    Add-CheckResult -Status "FAIL" -Message "Network API host has no authentication token."
}
else {
    Add-CheckResult -Status "OK" -Message "API bind/auth configuration is safe for the selected host."
}

try {
    $listener = Get-NetTCPConnection -State Listen -LocalPort $apiPort -ErrorAction SilentlyContinue
    if ($null -eq $listener) {
        Add-Failure "Port $apiPort is not listening." "Start API mit: start_friday_api.bat"
        Add-CheckResult -Status "FAIL" -Message "Port $apiPort is not listening."
    }
    else {
        Write-OutputLine "Port $apiPort is listening." Green
        Add-CheckResult -Status "OK" -Message "Port $apiPort is listening."
    }
}
catch {
    Add-Failure "Could not check TCP port $apiPort. $_" "Prüfe Berechtigungen / PowerShell-Session und wiederhole den Check"
    Add-CheckResult -Status "FAIL" -Message "Could not verify port $apiPort."
}

foreach ($endpoint in $endpoints) {
    $url = "$baseUrl$endpoint"
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 5 -Headers $apiHeaders -ErrorAction Stop
        if ($response.PSObject.Properties.Name -contains "ok" -and $response.ok -eq $true) {
            Write-OutputLine "OK: $endpoint" Green
            Add-CheckResult -Status "OK" -Message "$endpoint returned ok=true."
        }
        elseif ($response.PSObject.Properties.Name -contains "ok") {
            Add-Failure "$endpoint returned ok=$($response.ok)." "Prüfe den API-Server-Log und die Rückgabe dieser Route"
            Add-CheckResult -Status "FAIL" -Message "$endpoint returned ok=$($response.ok)."
        }
        else {
            Add-Failure "$endpoint does not expose the required 'ok' field." "Überprüfe API-Vertragskonvention (wrapper { ok, data })"
            Add-CheckResult -Status "FAIL" -Message "$endpoint does not expose required 'ok' field."
        }
    }
    catch {
        $exception = $_.Exception
        Add-Failure (
            "Request failed for $endpoint. $($exception.Message)"
        ) (
            Get-EndpunktFailureRecommendation -Endpoint $endpoint -Error $exception
        )
        Add-CheckResult -Status "FAIL" -Message "Request failed for $endpoint."
    }
}

Add-WarningIfMissingPath -PathToCheck (Join-Path $mobileDir "node_modules") -MessageIfMissing "friday-mobile/node_modules fehlt. Bitte in friday-mobile 'npm install' ausführen."
Add-WarningIfMissingPath -PathToCheck (Join-Path $desktopDir "node_modules") -MessageIfMissing "friday-desktop/node_modules fehlt. Bitte in friday-desktop 'npm install' ausführen."
Add-WarningIfMissingPath -PathToCheck (Join-Path $projectRoot "start_friday_stack.bat") -MessageIfMissing "start_friday_stack.bat fehlt im Projektroot."

if (Test-Path $mobileEnvPath) {
    $mobileApiUrl = $null
    foreach ($line in Get-Content $mobileEnvPath -ErrorAction SilentlyContinue) {
        $parsed = Parse-EnvValue -Line $line
        if ($parsed.Key -eq "EXPO_PUBLIC_FRIDAY_API_URL") {
            $mobileApiUrl = $parsed.Value
            break
        }
    }

    if (-not $mobileApiUrl) {
        $warning = "friday-mobile/.env hat keine EXPO_PUBLIC_FRIDAY_API_URL. Beispiel: EXPO_PUBLIC_FRIDAY_API_URL=http://127.0.0.1:8000"
        $warnings.Add($warning)
        Add-CheckResult -Status "WARN" -Message $warning
    }
    else {
        try {
            $uri = [System.Uri]$mobileApiUrl
            if ($uri.Port -ne [int]$apiPort) {
                $warnings.Add("EXPO_PUBLIC_FRIDAY_API_URL verweist auf Port '$($uri.Port)' statt '$apiPort'.")
                Add-CheckResult -Status "WARN" -Message "EXPO_PUBLIC_FRIDAY_API_URL uses port '$($uri.Port)' instead of '$apiPort'."
            }
            else {
                Add-CheckResult -Status "OK" -Message "EXPO_PUBLIC_FRIDAY_API_URL uses API port $apiPort."
            }

            if (
                $uri.Host -notin @("127.0.0.1", "localhost", "10.0.2.2") -and
                $uri.Host -notlike "192.168.*" -and
                $uri.Host -notlike "10.*" -and
                $uri.Host -notlike "172.*"
            ) {
                $warnings.Add("EXPO_PUBLIC_FRIDAY_API_URL verwendet Host '$($uri.Host)'. Für Gerät-Tests meist LAN-IP (192.168.x.x) verwenden.")
                Add-CheckResult -Status "WARN" -Message "EXPO_PUBLIC_FRIDAY_API_URL uses host '$($uri.Host)' (not local default)."
            }
            else {
                Add-CheckResult -Status "OK" -Message "EXPO_PUBLIC_FRIDAY_API_URL host '$($uri.Host)' is a local-friendly value."
            }
            if ($uri.Host -eq "127.0.0.1" -or $uri.Host -eq "localhost") {
            Write-OutputLine "Mobile API URL: $mobileApiUrl" Green
            }
            elseif ($uri.Host -eq "10.0.2.2") {
                Write-OutputLine "Mobile API URL (Android Emulator): $mobileApiUrl" Green
            }
            else {
                Write-OutputLine "Mobile API URL: $mobileApiUrl" Green
            }
        }
        catch {
            $warning = "EXPO_PUBLIC_FRIDAY_API_URL in friday-mobile/.env ist keine gültige URL."
            $warnings.Add($warning)
            Add-CheckResult -Status "WARN" -Message $warning
        }
    }
}
else {
    $warning = "friday-mobile/.env fehlt. Bitte 'copy .env.example .env' in friday-mobile ausführen."
    $warnings.Add($warning)
    Add-CheckResult -Status "WARN" -Message $warning
}

Add-CheckResult -Status "OK" -Message "Verifying API host '$apiHost' on port $apiPort."

if ($failed.Count -gt 0) {
    Write-OutputLine ""
    Write-OutputLine "Summary:" -ForegroundColor Cyan -Always
    $checkResults | ForEach-Object { Write-Host $_ }
    Write-OutputLine ""
    Write-OutputLine "[FAIL] Verification failed ($($checkCounts['FAIL']) failed, $($checkCounts['WARN']) warnings, $($checkCounts['OK']) checks ok)." -ForegroundColor Red -Always
    Write-OutputLine "Verification failed:" -ForegroundColor Red -Always
    $failed | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
    Write-OutputLine ""
    Write-OutputLine "Mögliche nächste Schritte:" -ForegroundColor Yellow -Always
    $recommendations | Sort-Object -Unique | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
    Write-SummaryJson -Status "FAIL"
    exit 1
}

Write-OutputLine ""
Write-OutputLine "Summary:" -ForegroundColor Cyan -Always
$checkResults | ForEach-Object { Write-Host $_ }

$statusLine = if ($checkCounts["WARN"] -gt 0) {
    "[WARN] Verification completed with $($checkCounts["WARN"]) warning(s)."
} else {
    "[OK] Verification completed without warnings."
}

Write-Host ""
if ($checkCounts["WARN"] -gt 0) {
    Write-OutputLine $statusLine -ForegroundColor Yellow -Always
}
else {
    Write-OutputLine $statusLine -ForegroundColor Green -Always
}

Write-OutputLine "All API checks passed." -ForegroundColor Green -Always

if ($warnings.Count -gt 0) {
    Write-OutputLine ""
    Write-OutputLine "Warnings (non-blocking):" -ForegroundColor Yellow -Always
    $warnings | ForEach-Object { Write-OutputLine " - $_" Yellow -Always }
}
else {
    Write-OutputLine "Optional frontend preflight checks found no issues." -ForegroundColor Green -Always
}

Write-SummaryJson -Status "OK"
exit 0
