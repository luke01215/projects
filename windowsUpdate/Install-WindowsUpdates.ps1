<#
.SYNOPSIS
    Checks for and installs Windows updates using the Windows Update COM object.

.DESCRIPTION
    This script uses the Microsoft.Update.Session COM object to search for,
    download, and install available Windows updates. Designed to be run
    via Jenkins or Task Scheduler on system startup.

.EXAMPLE
    .\Install-WindowsUpdates.ps1

.NOTES
    Requires administrator privileges.
    Logs output to console and can be redirected for Jenkins logging.
#>

[CmdletBinding()]
param()

# Ensure script is running with administrator privileges
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script requires administrator privileges. Please run as Administrator."
    exit 1
}

# Start logging
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "[$timestamp] Starting Windows Update check and installation..." -ForegroundColor Cyan

try {
    # Create Windows Update Session
    Write-Host "[$timestamp] Creating Windows Update session..." -ForegroundColor Yellow
    $updateSession = New-Object -ComObject Microsoft.Update.Session
    $updateSearcher = $updateSession.CreateUpdateSearcher()

    # Search for updates
    Write-Host "[$timestamp] Searching for available updates..." -ForegroundColor Yellow
    $searchResult = $updateSearcher.Search("IsInstalled=0 and Type='Software' and IsHidden=0")
    
    if ($searchResult.Updates.Count -eq 0) {
        Write-Host "[$timestamp] No updates available. System is up to date." -ForegroundColor Green
        exit 0
    }

    Write-Host "[$timestamp] Found $($searchResult.Updates.Count) update(s) available:" -ForegroundColor Cyan
    foreach ($update in $searchResult.Updates) {
        Write-Host "  - $($update.Title)" -ForegroundColor White
    }

    # Create collection of updates to download
    $updatesToDownload = New-Object -ComObject Microsoft.Update.UpdateColl
    foreach ($update in $searchResult.Updates) {
        if (-not $update.IsDownloaded) {
            $updatesToDownload.Add($update) | Out-Null
        }
    }

    # Download updates if needed
    if ($updatesToDownload.Count -gt 0) {
        Write-Host "[$timestamp] Downloading $($updatesToDownload.Count) update(s)..." -ForegroundColor Yellow
        $downloader = $updateSession.CreateUpdateDownloader()
        $downloader.Updates = $updatesToDownload
        $downloadResult = $downloader.Download()
        
        if ($downloadResult.ResultCode -eq 2) {
            Write-Host "[$timestamp] Download completed successfully." -ForegroundColor Green
        } else {
            Write-Warning "[$timestamp] Download completed with result code: $($downloadResult.ResultCode)"
        }
    } else {
        Write-Host "[$timestamp] All updates already downloaded." -ForegroundColor Green
    }

    # Create collection of updates to install
    $updatesToInstall = New-Object -ComObject Microsoft.Update.UpdateColl
    foreach ($update in $searchResult.Updates) {
        if ($update.IsDownloaded) {
            $updatesToInstall.Add($update) | Out-Null
        }
    }

    # Install updates
    if ($updatesToInstall.Count -gt 0) {
        Write-Host "[$timestamp] Installing $($updatesToInstall.Count) update(s)..." -ForegroundColor Yellow
        $installer = $updateSession.CreateUpdateInstaller()
        $installer.Updates = $updatesToInstall
        $installResult = $installer.Install()
        
        Write-Host "[$timestamp] Installation completed with result code: $($installResult.ResultCode)" -ForegroundColor Cyan
        
        # Result codes: 2 = Succeeded, 3 = Succeeded with errors, 4 = Failed, 5 = Aborted
        if ($installResult.ResultCode -eq 2) {
            Write-Host "[$timestamp] All updates installed successfully." -ForegroundColor Green
        } elseif ($installResult.ResultCode -eq 3) {
            Write-Warning "[$timestamp] Updates installed with some errors."
        } else {
            Write-Error "[$timestamp] Update installation failed with code: $($installResult.ResultCode)"
        }
        
        # Check if reboot is required
        if ($installResult.RebootRequired) {
            Write-Host "[$timestamp] REBOOT REQUIRED to complete update installation." -ForegroundColor Red
            Write-Host "[$timestamp] Please restart the computer at your earliest convenience." -ForegroundColor Red
            exit 3010  # Standard exit code for "reboot required"
        } else {
            Write-Host "[$timestamp] No reboot required." -ForegroundColor Green
        }
    } else {
        Write-Warning "[$timestamp] No updates ready to install."
    }

    $endTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$endTimestamp] Windows Update process completed." -ForegroundColor Cyan

} catch {
    $errorTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Error "[$errorTimestamp] An error occurred: $_"
    Write-Error $_.ScriptStackTrace
    exit 1
} finally {
    # Cleanup COM objects
    if ($updateSession) { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($updateSession) | Out-Null }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

exit 0
