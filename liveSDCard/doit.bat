@echo off
setlocal
:: ---------------------------------------------------------------------------
:: Launch PowerShell sync engine (full UNC network path support + time checks)
:: ---------------------------------------------------------------------------
set "PS_SCRIPT=%~dp0Sync-SDCard.ps1"
if not exist "%PS_SCRIPT%" set "PS_SCRIPT=%~dp0liveSDCard\Sync-SDCard.ps1"
if not exist "%PS_SCRIPT%" set "PS_SCRIPT=%~dp0..\liveSDCard\Sync-SDCard.ps1"
if not exist "%PS_SCRIPT%" (
    echo [ERROR] Could not find Sync-SDCard.ps1 alongside %~nx0.
    pause
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*
exit /b %ERRORLEVEL%
