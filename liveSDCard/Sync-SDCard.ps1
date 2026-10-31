<#
.SYNOPSIS
    Canon EOS 4000D - Bi-Directional SD Card Sync & Rigorous Log Inspector
    Supports UNC network paths and local drive paths.
#>

[CmdletBinding()]
param(
    [string]$CardDrive = "W:",
    [string]$RepoPath = ""
)

$Host.UI.RawUI.WindowTitle = "Canon EOS 4000D - SD Sync [$CardDrive]"
$ErrorActionPreference = "Continue"

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "  Canon EOS 4000D - SD Sync with Rigorous Timestamp Analysis" -ForegroundColor Cyan
Write-Host "  Current PC Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss.ff')" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# 1. Resolve Repository Root
# ---------------------------------------------------------------------------
$CandidateRoots = @(
    $RepoPath,
    $PSScriptRoot,
    (Split-Path -Parent $PSScriptRoot)
) | Where-Object { $_ -and (Test-Path $_) }

$Root = $null
foreach ($c in $CandidateRoots) {
    if (Test-Path (Join-Path $c "liveSDCard\autoexec.bin")) {
        $Root = (Get-Item $c).FullName
        break
    }
}

if (-not $Root) {
    Write-Host "[ERROR] Could not locate repo root containing liveSDCard\autoexec.bin" -ForegroundColor Red
    Write-Host "        Searched: $($CandidateRoots -join ', ')" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

$Src = Join-Path $Root "liveSDCard"
$Backup = Join-Path $Root "sd_card_backup"
$BackupLogs = Join-Path $Backup "logs"
$BackupSessions = Join-Path $Backup "sessions"

Write-Host "[OK] Repo Root : $Root" -ForegroundColor Green
Write-Host "[OK] Source    : $Src" -ForegroundColor Green
Write-Host "[OK] Backup    : $Backup" -ForegroundColor Green
Write-Host "[OK] SD Card   : $CardDrive" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 2. Check SD Card Presence
# ---------------------------------------------------------------------------
if (-not (Test-Path $CardDrive)) {
    Write-Host "`n[ERROR] SD card drive $CardDrive not found!" -ForegroundColor Red
    Write-Host "        Insert SD card into PC card reader and try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Ensure backup directories exist
$null = New-Item -ItemType Directory -Path $BackupLogs -Force -ErrorAction SilentlyContinue
$null = New-Item -ItemType Directory -Path $BackupSessions -Force -ErrorAction SilentlyContinue

# ---------------------------------------------------------------------------
# 3. PHASE 1: PULL Logs from SD Card with Timestamp Validation
# ---------------------------------------------------------------------------
Write-Host "`n[1/3] PULL logs from $CardDrive with Rigorous Timestamp Analysis" -ForegroundColor Yellow

$CardAutoexecPath = Join-Path $CardDrive "autoexec.bin"
$CardAutoexecTime = $null
if (Test-Path $CardAutoexecPath) {
    $CardAutoexec = Get-Item $CardAutoexecPath
    $CardAutoexecTime = $CardAutoexec.LastWriteTime
    Write-Host "      SD autoexec.bin installed: $($CardAutoexecTime.ToString('yyyy-MM-dd HH:mm:ss')) ($($CardAutoexec.Length) bytes)" -ForegroundColor Gray
}

$LogExtensions = @("*.LOG", "*.TXT", "*.DAT")
$CardLogs = @()
foreach ($ext in $LogExtensions) {
    $found = Get-ChildItem -Path $CardDrive -Filter $ext -File -ErrorAction SilentlyContinue
    if ($found) { $CardLogs += $found }
}

$SessionTimestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$SessionDir = Join-Path $BackupSessions $SessionTimestamp
$null = New-Item -ItemType Directory -Path $SessionDir -Force -ErrorAction SilentlyContinue

$PulledCount = 0
$PullFail = $false

if ($CardLogs.Count -eq 0) {
    Write-Host "      No root log files found on $CardDrive." -ForegroundColor Gray
} else {
    foreach ($log in $CardLogs) {
        $ageStr = ""
        $isFresh = $false
        if ($CardAutoexecTime) {
            $diffSec = ($log.LastWriteTime - $CardAutoexecTime).TotalSeconds
            if ($diffSec -ge 0) {
                $isFresh = $true
                $ageStr = "[FRESH: +$([math]::Round($diffSec))s after build flash]"
            } else {
                $ageStr = "[STALE: $([math]::Round(-$diffSec))s BEFORE build flash]"
            }
        }

        $destFile = Join-Path $BackupLogs $log.Name
        $sessionFile = Join-Path $SessionDir $log.Name
        try {
            Copy-Item -Path $log.FullName -Destination $destFile -Force
            Copy-Item -Path $log.FullName -Destination $sessionFile -Force
            $PulledCount++

            $color = if ($isFresh) { [ConsoleColor]::Green } else { [ConsoleColor]::Yellow }
            Write-Host ("      {0,-15} {1,7} bytes  {2}  {3}" -f $log.Name, $log.Length, $log.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'), $ageStr) -ForegroundColor $color
        } catch {
            Write-Host "      [FAIL] Could not pull $($log.Name): $_" -ForegroundColor Red
            $PullFail = $true
        }
    }
}

# Pull ML/LOGS and ML/SETTINGS if present
$CardMlLogs = Join-Path $CardDrive "ML\LOGS"
if (Test-Path $CardMlLogs) {
    $destMlLogs = Join-Path $BackupLogs "ml_logs"
    $null = New-Item -ItemType Directory -Path $destMlLogs -Force -ErrorAction SilentlyContinue
    Copy-Item -Path (Join-Path $CardMlLogs "*") -Destination $destMlLogs -Recurse -Force -ErrorAction SilentlyContinue
    Copy-Item -Path (Join-Path $CardMlLogs "*") -Destination (Join-Path $SessionDir "ml_logs") -Recurse -Force -ErrorAction SilentlyContinue
}

$CardMlSettings = Join-Path $CardDrive "ML\SETTINGS"
if (Test-Path $CardMlSettings) {
    $destMlSettings = Join-Path $Backup "settings"
    $null = New-Item -ItemType Directory -Path $destMlSettings -Force -ErrorAction SilentlyContinue
    Copy-Item -Path (Join-Path $CardMlSettings "*") -Destination $destMlSettings -Recurse -Force -ErrorAction SilentlyContinue
}

# Photos count
$Photos = @(Get-ChildItem -Path (Join-Path $CardDrive "DCIM") -Include "*.JPG", "*.CR2" -Recurse -File -ErrorAction SilentlyContinue).Count
Write-Host "      Pulled $PulledCount file(s) | Archived snapshot -> $SessionDir" -ForegroundColor Cyan
Write-Host "      Photos on card: $Photos" -ForegroundColor Gray

# If BUTTONS.LOG was pulled, preview the last 5 events
$PulledBtnLog = Join-Path $BackupLogs "BUTTONS.LOG"
if (Test-Path $PulledBtnLog) {
    $btnLines = @(Get-Content -Path $PulledBtnLog -ErrorAction SilentlyContinue)
    if ($btnLines.Count -gt 0) {
        Write-Host "`n      --- [BUTTONS.LOG Last Events ($($btnLines.Count) total)] ---" -ForegroundColor DarkCyan
        $previewCount = [Math]::Min(8, $btnLines.Count)
        $btnLines[($btnLines.Count - $previewCount)..($btnLines.Count - 1)] | ForEach-Object {
            Write-Host "      $_" -ForegroundColor DarkGray
        }
        Write-Host "      --------------------------------------------------------" -ForegroundColor DarkCyan
    }
}

# ---------------------------------------------------------------------------
# 4. PHASE 2: PUSH Build to SD Card (Atomic write + SHA256 Verification)
# ---------------------------------------------------------------------------
Write-Host "`n[2/3] PUSH build to $CardDrive" -ForegroundColor Yellow

# Clean obsolete FIR and test dumps from card root
$Obsolete = @("autoexec_*.bin", "bootflag_payload.bin", "ROM*.BIN", "ROM*.MD5", "*.FIR", "autoexec.tmp")
foreach ($pat in $Obsolete) {
    Remove-Item -Path (Join-Path $CardDrive $pat) -Force -ErrorAction SilentlyContinue
}

$SourceBinPath = Join-Path $Src "autoexec.bin"
if (-not (Test-Path $SourceBinPath)) {
    Write-Host "[ERROR] Source binary missing: $SourceBinPath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

$SourceBin = Get-Item $SourceBinPath
$SourceHash = (Get-FileHash -Path $SourceBinPath -Algorithm SHA256).Hash
Write-Host "      Source autoexec.bin : $($SourceBin.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss')) ($($SourceBin.Length) bytes)" -ForegroundColor Gray
Write-Host "      SHA256 Source       : $SourceHash" -ForegroundColor Gray

# Atomic copy: copy to .tmp, verify hash, then rename
$TargetTmp = Join-Path $CardDrive "autoexec.tmp"
$TargetBin = Join-Path $CardDrive "autoexec.bin"

Copy-Item -Path $SourceBinPath -Destination $TargetTmp -Force
$TmpHash = (Get-FileHash -Path $TargetTmp -Algorithm SHA256).Hash

if ($TmpHash -ne $SourceHash) {
    Write-Host "[ERROR] SHA256 verification failed on temporary write! Aborting push." -ForegroundColor Red
    Remove-Item $TargetTmp -Force -ErrorAction SilentlyContinue
    Read-Host "Press Enter to exit"
    exit 1
}

Move-Item -Path $TargetTmp -Destination $TargetBin -Force
$FinalHash = (Get-FileHash -Path $TargetBin -Algorithm SHA256).Hash

if ($FinalHash -ne $SourceHash) {
    Write-Host "[ERROR] Final SHA256 on card does NOT match source!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "      SHA256 on card      : $FinalHash" -ForegroundColor Green
Write-Host "      [OK] autoexec.bin VERIFIED IDENTICAL" -ForegroundColor Green

# Sync TESTS.CFG if present
$SourceCfg = Join-Path $Src "TESTS.CFG"
if (Test-Path $SourceCfg) {
    Copy-Item -Path $SourceCfg -Destination (Join-Path $CardDrive "TESTS.CFG") -Force
}

# Sync ML folder
$SourceMl = Join-Path $Src "ML"
$TargetMl = Join-Path $CardDrive "ML"
if (Test-Path $SourceMl) {
    $null = New-Item -ItemType Directory -Path $TargetMl -Force -ErrorAction SilentlyContinue
    # Robocopy mirror excluding logs and settings
    robocopy $SourceMl $TargetMl /E /XO /XD LOGS SETTINGS /R:1 /W:1 /NP /NFL /NDL >$null
    Write-Host "      [OK] ML folder synced" -ForegroundColor Green
}

# Ensure standard DCIM and MISC exist
$null = New-Item -ItemType Directory -Path (Join-Path $CardDrive "DCIM") -Force -ErrorAction SilentlyContinue
$null = New-Item -ItemType Directory -Path (Join-Path $CardDrive "MISC") -Force -ErrorAction SilentlyContinue

# ---------------------------------------------------------------------------
# 5. PHASE 3: Archive logs on card & self-update launchers
# ---------------------------------------------------------------------------
Write-Host "`n[3/3] Finalize" -ForegroundColor Yellow

if ($PullFail) {
    Write-Host "      [WARN] Log pull had errors - old logs left on card untouched." -ForegroundColor Yellow
} else {
    $CardArchiveDir = Join-Path $CardDrive "ML\LOGS\archive"
    $null = New-Item -ItemType Directory -Path $CardArchiveDir -Force -ErrorAction SilentlyContinue
    foreach ($log in $CardLogs) {
        $archiveTarget = Join-Path $CardArchiveDir $log.Name
        Copy-Item -Path $log.FullName -Destination $archiveTarget -Force -ErrorAction SilentlyContinue
        Remove-Item -Path $log.FullName -Force -ErrorAction SilentlyContinue
    }
    Write-Host "      Old logs archived to $CardArchiveDir (card starts clean on next boot)." -ForegroundColor Green
}

# Update launchers on card
$LocalScript = $PSCommandPath
if ($LocalScript -and (Test-Path $LocalScript)) {
    Copy-Item -Path $LocalScript -Destination (Join-Path $CardDrive "Sync-SDCard.ps1") -Force -ErrorAction SilentlyContinue
}
$BatWrapper = Join-Path $Src "doit.bat"
if (Test-Path $BatWrapper) {
    Copy-Item -Path $BatWrapper -Destination (Join-Path $CardDrive "doit.bat") -Force -ErrorAction SilentlyContinue
}
Write-Host "      Launchers updated on $CardDrive (Sync-SDCard.ps1 & doit.bat)." -ForegroundColor Gray

Write-Host "`n===============================================================================" -ForegroundColor Cyan
Write-Host "  DONE. Eject $CardDrive, boot the camera, test buttons, then re-run to pull logs." -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
