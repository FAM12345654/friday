$ErrorActionPreference = "Stop"

try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
    $OutputEncoding = [Console]::OutputEncoding
}
catch {
    # Keep the readiness check running if the shell cannot change encoding.
}

$projectRoot = $PSScriptRoot
$mobileRoot = Join-Path $projectRoot "friday-mobile"
$packagePath = Join-Path $mobileRoot "package.json"
$appConfigPath = Join-Path $mobileRoot "app.json"
$easConfigPath = Join-Path $mobileRoot "eas.json"
$envPath = Join-Path $mobileRoot ".env"
$appJsConfigPath = Join-Path $mobileRoot "app.config.js"

$failed = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

function Add-Result {
    param(
        [ValidateSet("OK", "WARN", "FAIL")]
        [string]$Status,
        [string]$Message
    )

    if ($Status -eq "FAIL") {
        $failed.Add($Message)
    }
    elseif ($Status -eq "WARN") {
        $warnings.Add($Message)
    }

    Write-Host "[$Status] $Message"
}

function Read-JsonFile {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return $null
    }

    return (Get-Content -Raw $Path | ConvertFrom-Json)
}

Write-Host "Friday mobile release readiness"
Write-Host "Mobile root: $mobileRoot"
Write-Host ""

$packageJson = Read-JsonFile -Path $packagePath
if ($null -eq $packageJson) {
    Add-Result -Status "FAIL" -Message "friday-mobile/package.json fehlt."
}
else {
    Add-Result -Status "OK" -Message "package.json gefunden."
    if ($packageJson.dependencies.PSObject.Properties.Name -contains "expo-updates") {
        Add-Result -Status "OK" -Message "expo-updates ist installiert."
    }
    else {
        Add-Result -Status "FAIL" -Message "expo-updates fehlt. Bitte in friday-mobile 'npx expo install expo-updates' ausführen."
    }
    if ($packageJson.dependencies.PSObject.Properties.Name -contains "expo-secure-store") {
        Add-Result -Status "OK" -Message "expo-secure-store ist als native Abhängigkeit installiert."
    }
    else {
        Add-Result -Status "FAIL" -Message "expo-secure-store fehlt; API-Token darf nicht unsicher gespeichert werden."
    }
}

$appConfig = Read-JsonFile -Path $appConfigPath
if ($null -eq $appConfig) {
    Add-Result -Status "FAIL" -Message "friday-mobile/app.json fehlt."
}
else {
    Add-Result -Status "OK" -Message "app.json gefunden."
    if ($appConfig.expo.android.package) {
        Add-Result -Status "OK" -Message "Android package gesetzt: $($appConfig.expo.android.package)"
    }
    else {
        Add-Result -Status "FAIL" -Message "Android package fehlt."
    }

    if ($appConfig.expo.ios.bundleIdentifier) {
        Add-Result -Status "OK" -Message "iOS bundleIdentifier gesetzt: $($appConfig.expo.ios.bundleIdentifier)"
    }
    else {
        Add-Result -Status "WARN" -Message "iOS bundleIdentifier fehlt."
    }

    if ($appConfig.expo.runtimeVersion -and $appConfig.expo.runtimeVersion -ne "1.0.0-sdk54") {
        Add-Result -Status "OK" -Message "runtimeVersion trennt den SecureStore-Build vom Legacy-Build."
    }
    else {
        Add-Result -Status "FAIL" -Message "runtimeVersion fehlt oder entspricht noch dem inkompatiblen Build-15-Legacywert."
    }

    $buildProperties = @($appConfig.expo.plugins) | Where-Object {
        $_ -is [System.Array] -and $_[0] -eq "expo-build-properties"
    } | Select-Object -First 1
    if ($buildProperties -and $buildProperties[1].android.usesCleartextTraffic -eq $false) {
        Add-Result -Status "OK" -Message "Android-Cleartext ist deaktiviert."
    }
    else {
        Add-Result -Status "FAIL" -Message "Android-Cleartext muss deaktiviert sein."
    }

    if ($appConfig.expo.updates.enabled -eq $true -and $appConfig.expo.updates.checkAutomatically -eq "ON_LOAD") {
        Add-Result -Status "OK" -Message "Updates sind für App-Start-Check aktiviert."
    }
    else {
        Add-Result -Status "FAIL" -Message "updates.enabled/checkAutomatically ist nicht auf automatische Update-Prüfung gesetzt."
    }

    if ($appConfig.expo.updates.url -and $appConfig.expo.extra.eas.projectId) {
        Add-Result -Status "OK" -Message "EAS Update URL und projectId sind konfiguriert."
    }
    else {
        Add-Result -Status "FAIL" -Message "EAS Update ist noch nicht mit Projekt-ID verbunden. Ausführen: cd friday-mobile && npm run eas:configure"
    }
}

if ((Test-Path $appJsConfigPath) -and (Get-Content -Raw $appJsConfigPath) -match "expo-secure-store") {
    Add-Result -Status "OK" -Message "expo-secure-store ist im nativen Expo-Plugin-Set registriert."
}
else {
    Add-Result -Status "FAIL" -Message "expo-secure-store fehlt im nativen Expo-Plugin-Set."
}

$easConfig = Read-JsonFile -Path $easConfigPath
if ($null -eq $easConfig) {
    Add-Result -Status "FAIL" -Message "friday-mobile/eas.json fehlt."
}
else {
    Add-Result -Status "OK" -Message "eas.json gefunden."
    if ($easConfig.build.preview.distribution -eq "internal" -and $easConfig.build.preview.android.buildType -eq "apk") {
        Add-Result -Status "OK" -Message "Android Preview Build ist direkt installierbar (internal APK)."
    }
    else {
        Add-Result -Status "FAIL" -Message "Preview Build ist nicht als internal APK konfiguriert."
    }

    if ($easConfig.build.preview.channel -eq "preview" -and $easConfig.build.production.channel -eq "production") {
        Add-Result -Status "OK" -Message "Preview/Production Update-Kanäle sind gesetzt."
    }
    else {
        Add-Result -Status "FAIL" -Message "EAS Update-Kanäle preview/production fehlen."
    }
}

if (Test-Path $envPath) {
    $envContent = Get-Content -Raw $envPath
    if ($envContent -match "EXPO_PUBLIC_FRIDAY_API_URL=http://192\.168\.x\.x") {
        Add-Result -Status "WARN" -Message "friday-mobile/.env nutzt noch den Platzhalter 192.168.x.x."
    }
    elseif ($envContent -match "EXPO_PUBLIC_FRIDAY_API_URL=") {
        $urlMatch = [regex]::Match($envContent, "(?m)^EXPO_PUBLIC_FRIDAY_API_URL=([^\r\n]+)")
        $apiUrl = $urlMatch.Groups[1].Value.Trim().Trim('"')
        try {
            $uri = [Uri]$apiUrl
            if ($uri.Scheme -ne "https") {
                Add-Result -Status "FAIL" -Message "Mobile API muss HTTPS verwenden."
            }
            else {
                Add-Result -Status "OK" -Message "Mobile API verwendet HTTPS."
            }
            $token = [string]$env:FRIDAY_API_TOKEN
            if ([string]::IsNullOrWhiteSpace($token)) {
                $token = [string][Environment]::GetEnvironmentVariable("FRIDAY_API_TOKEN", "User")
            }
            $headers = @{}
            if (-not [string]::IsNullOrWhiteSpace($token)) {
                $headers.Authorization = "Bearer $($token.Trim())"
            }
            $health = Invoke-RestMethod -Uri "$apiUrl/health" -TimeoutSec 8 -ErrorAction Stop
            $contract = Invoke-RestMethod -Uri "$apiUrl/api/setup/status" -Headers $headers -TimeoutSec 8 -ErrorAction Stop
            if ($health.ok -eq $true -and $contract.ok -eq $true) {
                Add-Result -Status "OK" -Message "Mobile HTTPS-API und geschützter Vertragsendpunkt sind erreichbar."
            }
            else {
                Add-Result -Status "FAIL" -Message "Mobile HTTPS-API liefert nicht den erwarteten Vertrag."
            }
        }
        catch {
            Add-Result -Status "FAIL" -Message "Mobile HTTPS-API ist nicht vollständig erreichbar: $($_.Exception.Message)"
        }
    }
    else {
        Add-Result -Status "WARN" -Message "friday-mobile/.env enthält keine EXPO_PUBLIC_FRIDAY_API_URL."
    }
}
else {
    Add-Result -Status "WARN" -Message "friday-mobile/.env fehlt."
}

Write-Host ""
if ($failed.Count -gt 0) {
    Write-Host "[FAIL] Mobile Release ist noch nicht komplett download/update-ready."
    Write-Host "Nächste Schritte:"
    Write-Host " - cd friday-mobile"
    Write-Host " - npm run eas:login"
    Write-Host " - npm run eas:configure"
    Write-Host " - npm run build:android:preview"
    Write-Host " - npm run update:preview"
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host "[WARN] Mobile Release ist grundsätzlich vorbereitet, mit Warnungen."
    exit 0
}

Write-Host "[OK] Mobile Release ist download- und update-ready."
exit 0
