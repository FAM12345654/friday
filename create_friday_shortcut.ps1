$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

$ShortcutDefinitions = @(
    @{ Name = "Friday.lnk"; TargetFile = "start_friday.bat"; Description = "Start Friday local assistant" },
    @{ Name = "Friday Stack.lnk"; TargetFile = "start_friday_stack.bat"; Description = "Start API + Mobile + Desktop together" },
    @{ Name = "Friday API.lnk"; TargetFile = "start_friday_api.bat"; Description = "Start Friday FastAPI backend on :8000" },
    @{ Name = "Friday Mobile.lnk"; TargetFile = "start_friday_mobile.bat"; Description = "Start Friday Expo mobile app" },
    @{ Name = "Friday Desktop.lnk"; TargetFile = "start_friday_desktop.bat"; Description = "Start Friday Electron desktop app" },
    @{ Name = "Friday Desktop No API.lnk"; TargetFile = "start_friday_desktop_skip_api.bat"; Description = "Start Friday Electron desktop app without embedded API" },
    @{ Name = "Friday Verify.lnk"; TargetFile = "verify_friday_services_ci.bat"; Description = "Run Friday API verification (CI style, JSON-capable)" },
    @{ Name = "Friday Checklist.lnk"; TargetFile = "run_friday_checklist.bat"; Description = "Run Friday one-command checklist" },
    @{ Name = "Friday Mobile Release Check.lnk"; TargetFile = "verify_friday_mobile_release.bat"; Description = "Check whether Friday Mobile is download and update ready" },
    @{ Name = "Friday Tests.lnk"; TargetFile = "run_tests.bat"; Description = "Run Friday local tests" },
    @{ Name = "Friday Setup.lnk"; TargetFile = "setup_friday.bat"; Description = "Setup Friday local assistant" }
)

$DesktopCandidates = New-Object System.Collections.Generic.List[string]

$DefaultDesktop = [Environment]::GetFolderPath("Desktop")
if ($DefaultDesktop -and (Test-Path $DefaultDesktop)) {
    $DesktopCandidates.Add($DefaultDesktop)
}

if ($env:OneDrive) {
    $OneDriveDesktop = Join-Path $env:OneDrive "Desktop"
    if (Test-Path $OneDriveDesktop) {
        $DesktopCandidates.Add($OneDriveDesktop)
    }
}

$DesktopPaths = $DesktopCandidates | Select-Object -Unique

if (-not $DesktopPaths -or $DesktopPaths.Count -eq 0) {
    Write-Host "SHORTCUT_CREATED_FAILED"
    Write-Host "No valid Desktop folder was found."
    exit 1
}

$WScriptShell = New-Object -ComObject WScript.Shell
$CreatedCount = 0

foreach ($DesktopPath in $DesktopPaths) {
    Write-Host "Using Desktop folder:"
    Write-Host $DesktopPath

    foreach ($Definition in $ShortcutDefinitions) {
        $TargetPath = Join-Path $ProjectRoot $Definition.TargetFile
        $ShortcutPath = Join-Path $DesktopPath $Definition.Name

        if (-not (Test-Path $TargetPath)) {
            Write-Host "Missing target file:"
            Write-Host $TargetPath
            continue
        }

        $Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = $TargetPath
        $Shortcut.WorkingDirectory = $ProjectRoot
        $Shortcut.Description = $Definition.Description
        $Shortcut.Save()

        if (Test-Path $ShortcutPath) {
            $CreatedCount += 1
            Write-Host "Created shortcut:"
            Write-Host $ShortcutPath
        } else {
            Write-Host "Failed to verify shortcut:"
            Write-Host $ShortcutPath
        }
    }
}

if ($CreatedCount -gt 0) {
    Write-Host "SHORTCUT_CREATED_OK"
    Write-Host "Created shortcut count:"
    Write-Host $CreatedCount
} else {
    Write-Host "SHORTCUT_CREATED_FAILED"
    exit 1
}
