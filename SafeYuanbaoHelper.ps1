<#
.SYNOPSIS
Yuanbao Safe Memory Manager v3.0

.DESCRIPTION
Safely manage Yuanbao application and WebView2 processes without affecting running Yuanbao.
All operations require user confirmation for safety.

.FEATURES
1. System Status Check - View Yuanbao, WebView2, and system resource status
2. Safe Cleanup Mode - Clean orphan processes without affecting Yuanbao
3. Safe Monitor Mode - Monitor only, no cleanup
4. System Repair - Fix WebView2 configuration (requires admin)
5. One-Click Diagnose - Comprehensive system diagnosis
6. Edge Cleanup Tool - Clean high memory Edge processes
#>

function Show-MainMenu {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "    Yuanbao Safe Memory Manager v3.0" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " Safe Mode: Won't terminate running Yuanbao" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host " Please select a function:" -ForegroundColor White
    Write-Host ""
    Write-Host "  [1] System Status Check" -ForegroundColor Green
    Write-Host "      View Yuanbao, WebView2, system resources" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [2] Safe Cleanup Mode" -ForegroundColor Green
    Write-Host "      Clean orphan processes, protect Yuanbao" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [3] Safe Monitor Mode" -ForegroundColor Green
    Write-Host "      Monitor only, no termination" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [4] System Repair" -ForegroundColor Green
    Write-Host "      Fix WebView2 config (requires admin)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [5] One-Click Diagnose" -ForegroundColor Green
    Write-Host "      Comprehensive system diagnosis" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [6] Edge Cleanup Tool" -ForegroundColor Green
    Write-Host "      Clean high memory Edge processes" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [0] Exit" -ForegroundColor Gray
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " Tip: Recommend running [1] System Status Check first" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    
    $choice = Read-Host "`nPlease enter option (0-6)"
    return $choice
}

function Test-YuanBaoRunning {
    $yuanbaoProcess = Get-Process -Name "*yuanbao*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($yuanbaoProcess) {
        return $true, $yuanbaoProcess.Id
    }
    return $false, 0
}

function Pause-Wait {
    Write-Host "`nPress Enter to continue..." -ForegroundColor Gray
    $null = Read-Host
}

function Show-SuccessConfirm($message) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host $message -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Please confirm the result, then press Enter to return to main menu..." -ForegroundColor Yellow
    $null = Read-Host
}

function Start-SystemStatusCheck {
    Clear-Host
    Write-Host "Checking system status..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Gray
    
    $yuanbaoRunning, $yuanbaoPid = Test-YuanBaoRunning
    if ($yuanbaoRunning) {
        $yuanbaoProcess = Get-Process -Id $yuanbaoPid -ErrorAction SilentlyContinue
        if ($yuanbaoProcess) {
            $yuanbaoMem = [math]::Round($yuanbaoProcess.WorkingSet64 / 1MB, 2)
            Write-Host "Yuanbao Status: Running" -ForegroundColor Green
            Write-Host "  PID: $yuanbaoPid" -ForegroundColor Gray
            Write-Host "  Memory: ${yuanbaoMem} MB" -ForegroundColor Gray
        }
    } else {
        Write-Host "Yuanbao Status: Not Running" -ForegroundColor Gray
    }
    
    $webviewProcesses = Get-Process -Name "msedgewebview2" -ErrorAction SilentlyContinue
    Write-Host "`nWebView2 Processes: $($webviewProcesses.Count)" -ForegroundColor Green
    
    if ($webviewProcesses.Count -gt 0) {
        $totalMem = 0
        foreach ($proc in $webviewProcesses) {
            $procMem = [math]::Round($proc.WorkingSet64 / 1MB, 2)
            $totalMem += $procMem
        }
        Write-Host "  Total Memory: ${totalMem} MB" -ForegroundColor Gray
        Write-Host "  Average Memory: $([math]::Round($totalMem / $webviewProcesses.Count, 2)) MB" -ForegroundColor Gray
    }
    
    $edgeProcesses = Get-Process -Name "msedge" -ErrorAction SilentlyContinue
    Write-Host "`nEdge Processes: $($edgeProcesses.Count)" -ForegroundColor Green
    
    if ($edgeProcesses.Count -gt 0) {
        $highMemCount = 0
        foreach ($proc in $edgeProcesses) {
            if ($proc.WorkingSet64 -gt 500MB) {
                $highMemCount++
            }
        }
        if ($highMemCount -gt 0) {
            Write-Host "  High Memory Processes (>500MB): ${highMemCount}" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`nSystem Resources:" -ForegroundColor Green
    try {
        $os = Get-WmiObject Win32_OperatingSystem | Select-Object -First 1
        if ($os) {
            $totalMem = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
            $freeMem = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
            $usedMem = $totalMem - $freeMem
            $memPercent = [math]::Round(($usedMem / $totalMem) * 100, 2)
            
            Write-Host "  Total Memory: ${totalMem} GB" -ForegroundColor Gray
            Write-Host "  Used Memory: ${usedMem} GB" -ForegroundColor Gray
            Write-Host "  Available Memory: ${freeMem} GB" -ForegroundColor Gray
            Write-Host "  Memory Usage: ${memPercent}%" -ForegroundColor $(if ($memPercent -gt 80) { "Red" } else { "Green" })
        } else {
            Write-Host "  Unable to get memory info" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  Unable to get memory info" -ForegroundColor Yellow
    }
    
    Show-SuccessConfirm "System status check completed!"
}

function Start-SafeCleanup {
    Clear-Host
    Write-Host "Starting Safe Cleanup Mode..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Gray
    
    $yuanbaoRunning, $yuanbaoPid = Test-YuanBaoRunning
    
    if ($yuanbaoRunning) {
        Write-Host "WARNING: Yuanbao is running (PID: $yuanbaoPid)" -ForegroundColor Yellow
        Write-Host "Yuanbao processes will NOT be terminated" -ForegroundColor Yellow
    }
    
    Write-Host "`nThis function will clean orphan processes without affecting Yuanbao"
    Write-Host "Continue? (Y/N)" -ForegroundColor White
    
    $choice = Read-Host
    if ($choice -ne "Y" -and $choice -ne "y") {
        Write-Host "`nCleanup cancelled" -ForegroundColor Yellow
        Pause-Wait
        return
    }
    
    $cleanedCount = 0
    
    Write-Host "`n[1] Cleaning orphan WebView2 processes..." -ForegroundColor Green
    if ($yuanbaoRunning) {
        Write-Host "  SKIPPED (Yuanbao running, protecting)" -ForegroundColor Gray
    } else {
        $webviewProcesses = Get-Process -Name "msedgewebview2" -ErrorAction SilentlyContinue
        if ($webviewProcesses.Count -gt 0) {
            foreach ($proc in $webviewProcesses) {
                try {
                    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                    Write-Host "  CLEANED: PID $($proc.Id)" -ForegroundColor Gray
                    $cleanedCount++
                } catch {
                    Write-Host "  FAILED: PID $($proc.Id)" -ForegroundColor DarkGray
                }
            }
        } else {
            Write-Host "  NO orphan processes found" -ForegroundColor Green
        }
    }
    
    Write-Host "`n[2] Cleaning high memory Edge processes..." -ForegroundColor Green
    $edgeProcesses = Get-Process -Name "msedge" -ErrorAction SilentlyContinue | Where-Object { 
        $_.MainWindowTitle -eq "" -and $_.WorkingSet64 -gt 500MB
    }
    
    if ($edgeProcesses.Count -gt 0) {
        foreach ($proc in $edgeProcesses) {
            $mem = [math]::Round($proc.WorkingSet64 / 1MB, 1)
            try {
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                Write-Host "  CLEANED: ${mem}MB" -ForegroundColor Gray
                $cleanedCount++
            } catch {
                Write-Host "  FAILED: ${mem}MB" -ForegroundColor DarkGray
            }
        }
    } else {
        Write-Host "  NO high memory Edge processes" -ForegroundColor Green
    }
    
    Write-Host "`n[3] Cleaning temp files..." -ForegroundColor Green
    $tempCleaned = 0
    $tempPaths = @(
        "$env:TEMP\*WebView*",
        "$env:TEMP\*Edge*"
    )
    
    foreach ($path in $tempPaths) {
        if (Test-Path $path) {
            try {
                Get-ChildItem -Path $path -Recurse -ErrorAction SilentlyContinue | 
                    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-1) } | 
                    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
                $tempCleaned++
            } catch { }
        }
    }
    Write-Host "  CLEANED: ${tempCleaned} temp files" -ForegroundColor Green
    
    $resultMsg = "Total cleaned: $cleanedCount processes, $tempCleaned temp files"
    Show-SuccessConfirm $resultMsg
}

function Start-SafeMonitor {
    Clear-Host
    Write-Host "Starting Safe Monitor Mode..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Gray
    Write-Host " Monitor only, no cleanup" -ForegroundColor Green
    Write-Host " Press Ctrl+C to exit" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Gray
    
    $logFile = "$env:USERPROFILE\Desktop\Yuanbao_Monitor_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    $monitorCount = 0
    
    try {
        while ($true) {
            $monitorCount++
            $currentTime = Get-Date -Format "HH:mm:ss"
            
            Clear-Host
            Write-Host "Yuanbao Safe Monitor (Check ${monitorCount})" -ForegroundColor Cyan
            Write-Host "Time: $currentTime" -ForegroundColor Gray
            Write-Host "Log: $logFile" -ForegroundColor Gray
            Write-Host "========================================" -ForegroundColor Gray
            
            "$currentTime - Check ${monitorCount}" | Out-File $logFile -Append
            
            $yuanbaoRunning, $yuanbaoPid = Test-YuanBaoRunning
            if ($yuanbaoRunning) {
                Write-Host "Yuanbao: Running" -ForegroundColor Green
                "Yuanbao: Running (PID: $yuanbaoPid)" | Out-File $logFile -Append
            } else {
                Write-Host "Yuanbao: Not Running" -ForegroundColor Gray
                "Yuanbao: Not Running" | Out-File $logFile -Append
            }
            
            $webviewProcesses = Get-Process -Name "msedgewebview2" -ErrorAction SilentlyContinue
            $webviewCount = $webviewProcesses.Count
            
            if ($webviewCount -gt 0) {
                $totalMem = 0
                $webviewProcesses | ForEach-Object { $totalMem += [math]::Round($_.WorkingSet64 / 1MB, 2) }
                Write-Host "WebView2: ${webviewCount} processes" -ForegroundColor Green
                Write-Host "Total Memory: ${totalMem} MB" -ForegroundColor Gray
                "WebView2: ${webviewCount} processes, ${totalMem}MB" | Out-File $logFile -Append
            } else {
                Write-Host "WebView2: 0 processes" -ForegroundColor Green
                "WebView2: 0 processes" | Out-File $logFile -Append
            }
            
            try {
                $os = Get-WmiObject Win32_OperatingSystem | Select-Object -First 1
                if ($os) {
                    $totalMem = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
                    $freeMem = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
                    $usedMem = $totalMem - $freeMem
                    $memPercent = [math]::Round(($usedMem / $totalMem) * 100, 2)
                    
                    Write-Host "System Memory: ${memPercent}% used" -ForegroundColor $(if ($memPercent -gt 80) { "Red" } else { "Green" })
                    Write-Host "Available: ${freeMem} GB" -ForegroundColor Gray
                    
                    "System Memory: ${memPercent}%, Available: ${freeMem}GB" | Out-File $logFile -Append
                }
            } catch {
                Write-Host "System Memory: Unable to get" -ForegroundColor Yellow
            }
            
            Write-Host "`n========================================" -ForegroundColor Gray
            Write-Host "Monitoring... Press Ctrl+C to exit" -ForegroundColor Cyan
            
            "" | Out-File $logFile -Append
            
            for ($i = 30; $i -gt 0; $i--) {
                Write-Host "`rNext check: ${i}s  " -NoNewline -ForegroundColor Yellow
                Start-Sleep -Seconds 1
            }
        }
    } catch {
        Write-Host "`n========================================" -ForegroundColor Green
        Write-Host "  MONITOR STOPPED" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Total checks: ${monitorCount}" -ForegroundColor White
        Write-Host "Log file: $logFile" -ForegroundColor White
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Press Enter to return to main menu..." -ForegroundColor Gray
        $null = Read-Host
    }
}

function Start-SystemRepair {
    Clear-Host
    Write-Host "Starting System Repair..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Gray
    
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
        Write-Host "ERROR: Admin privileges required" -ForegroundColor Red
        Write-Host "Please run script as Administrator" -ForegroundColor Yellow
        Pause-Wait
        return
    }
    
    Write-Host "This will fix WebView2 configuration:"
    Write-Host "1. Clean WebView2 cache"
    Write-Host "2. Optimize registry settings"
    Write-Host "3. Reset environment variables"
    Write-Host ""
    Write-Host "Note: Won't affect running Yuanbao"
    Write-Host ""
    Write-Host "Continue? (Y/N)" -ForegroundColor White
    
    $choice = Read-Host
    if ($choice -ne "Y" -and $choice -ne "y") {
        Write-Host "`nRepair cancelled" -ForegroundColor Yellow
        Pause-Wait
        return
    }
    
    $yuanbaoRunning, $yuanbaoPid = Test-YuanBaoRunning
    if ($yuanbaoRunning) {
        Write-Host "Note: Yuanbao running, skipping process cleanup" -ForegroundColor Yellow
    }
    
    $fixedItems = 0
    
    Write-Host "`n[1] Cleaning cache..." -ForegroundColor Green
    if (-not $yuanbaoRunning) {
        $cachePaths = @(
            "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache",
            "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Code Cache"
        )
        
        foreach ($path in $cachePaths) {
            if (Test-Path $path) {
                try {
                    Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
                    Write-Host "  CLEANED: $path" -ForegroundColor Gray
                    $fixedItems++
                } catch {
                    Write-Host "  FAILED: $path" -ForegroundColor DarkGray
                }
            }
        }
    } else {
        Write-Host "  SKIPPED (Yuanbao running)" -ForegroundColor Gray
    }
    
    Write-Host "`n[2] Fixing registry..." -ForegroundColor Green
    try {
        $regPath = "HKCU:\Software\Microsoft\Edge\WebView2"
        if (-not (Test-Path $regPath)) {
            New-Item -Path $regPath -Force | Out-Null
        }
        
        Set-ItemProperty -Path $regPath -Name "DiskCacheSize" -Value 104857600 -ErrorAction SilentlyContinue
        Write-Host "  REGISTRY updated" -ForegroundColor Gray
        $fixedItems++
    } catch {
        Write-Host "  REGISTRY fix failed" -ForegroundColor DarkGray
    }
    
    Write-Host "`n[3] Setting environment variables..." -ForegroundColor Green
    try {
        [Environment]::SetEnvironmentVariable("WEBVIEW2_DISABLE_GPU", "0", "User")
        Write-Host "  ENVIRONMENT variables set" -ForegroundColor Gray
        $fixedItems++
    } catch {
        Write-Host "  ENVIRONMENT set failed" -ForegroundColor DarkGray
    }
    
    $resultMsg = "Fixed: ${fixedItems} items`nRecommend restarting Yuanbao for changes to take effect"
    Show-SuccessConfirm $resultMsg
}

function Start-SystemDiagnose {
    Clear-Host
    Write-Host "Running One-Click Diagnose..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Gray
    
    $results = @()
    
    Write-Host "`n[1] Checking Yuanbao..." -ForegroundColor Green
    $yuanbaoRunning, $yuanbaoPid = Test-YuanBaoRunning
    if ($yuanbaoRunning) {
        $yuanbaoProcess = Get-Process -Id $yuanbaoPid -ErrorAction SilentlyContinue
        if ($yuanbaoProcess) {
            $yuanbaoMem = [math]::Round($yuanbaoProcess.WorkingSet64 / 1MB, 2)
            Write-Host "  Yuanbao: Running" -ForegroundColor Green
            Write-Host "    Memory: ${yuanbaoMem} MB" -ForegroundColor Gray
            $results += "Yuanbao: Running (${yuanbaoMem}MB)"
        }
    } else {
        Write-Host "  Yuanbao: Not Running" -ForegroundColor Gray
        $results += "Yuanbao: Not Running"
    }
    
    Write-Host "`n[2] Checking WebView2..." -ForegroundColor Green
    $webviewProcesses = Get-Process -Name "msedgewebview2" -ErrorAction SilentlyContinue
    $webviewCount = $webviewProcesses.Count
    
    if ($webviewCount -gt 0) {
        $totalMem = 0
        $webviewProcesses | ForEach-Object { $totalMem += [math]::Round($_.WorkingSet64 / 1MB, 2) }
        $avgMem = [math]::Round($totalMem / $webviewCount, 2)
        
        Write-Host "  WebView2: ${webviewCount} processes" -ForegroundColor Green
        Write-Host "    Total Memory: ${totalMem} MB" -ForegroundColor Gray
        Write-Host "    Average Memory: ${avgMem} MB" -ForegroundColor Gray
        
        if ($avgMem -gt 200) {
            Write-Host "  WARNING: High average memory" -ForegroundColor Yellow
            $results += "WebView2: ${webviewCount} processes (High Memory)"
        } else {
            $results += "WebView2: ${webviewCount} processes (Normal)"
        }
    } else {
        Write-Host "  WebView2: No processes" -ForegroundColor Green
        $results += "WebView2: No processes"
    }
    
    Write-Host "`n[3] Checking System Resources..." -ForegroundColor Green
    try {
        $os = Get-WmiObject Win32_OperatingSystem | Select-Object -First 1
        if ($os) {
            $totalMem = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
            $freeMem = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
            $usedMem = $totalMem - $freeMem
            $memPercent = [math]::Round(($usedMem / $totalMem) * 100, 2)
            
            Write-Host "  Memory Usage: ${memPercent}%" -ForegroundColor $(if ($memPercent -gt 80) { "Yellow" } else { "Green" })
            Write-Host "    Available: ${freeMem} GB" -ForegroundColor Gray
            
            $results += "Memory: ${memPercent}% (Available: ${freeMem}GB)"
        } else {
            Write-Host "  WARNING: Unable to get memory info" -ForegroundColor Yellow
            $results += "Memory: Unable to get"
        }
    } catch {
        Write-Host "  WARNING: Unable to get memory info" -ForegroundColor Yellow
        $results += "Memory: Unable to get"
    }
    
    Write-Host "`n[4] Checking Disk Space..." -ForegroundColor Green
    $drive = Get-PSDrive -Name C -ErrorAction SilentlyContinue
    if ($drive) {
        $freeGB = [math]::Round($drive.Free / 1GB, 2)
        $freePercent = [math]::Round(($drive.Free / ($drive.Used + $drive.Free)) * 100, 2)
        
        Write-Host "  Drive C:" -ForegroundColor Green
        Write-Host "    Free Space: ${freeGB} GB" -ForegroundColor Gray
        Write-Host "    Free Percent: ${freePercent}%" -ForegroundColor Gray
        
        if ($freeGB -lt 10) {
            Write-Host "  WARNING: Low disk space" -ForegroundColor Yellow
            $results += "Disk: Low space (${freeGB}GB)"
        } else {
            $results += "Disk: Sufficient space (${freeGB}GB)"
        }
    }
    
    Write-Host "`n[5] Checking Network..." -ForegroundColor Green
    try {
        $ping = Test-NetConnection -ComputerName "www.qq.com" -InformationLevel Quiet -ErrorAction SilentlyContinue
        if ($ping) {
            Write-Host "  Network: Connected" -ForegroundColor Green
            $results += "Network: Connected"
        } else {
            Write-Host "  WARNING: Network issues" -ForegroundColor Yellow
            $results += "Network: Issues"
        }
    } catch {
        Write-Host "  WARNING: Network check failed" -ForegroundColor Yellow
        $results += "Network: Check failed"
    }
    
    Write-Host "`n========================================" -ForegroundColor Gray
    Write-Host "Diagnose Complete!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Gray
    Write-Host "Results:" -ForegroundColor White
    
    foreach ($result in $results) {
        Write-Host "  - $result" -ForegroundColor Gray
    }
    
    Write-Host "`nRecommendations:" -ForegroundColor White
    if ($webviewCount -gt 15) {
        Write-Host "  WARNING: Many WebView2 processes, consider cleanup when not using Yuanbao" -ForegroundColor Yellow
    } elseif (-not $yuanbaoRunning) {
        Write-Host "  INFO: Yuanbao not running, full system cleanup recommended" -ForegroundColor Blue
    } else {
        Write-Host "  INFO: Yuanbao running, use safe cleanup mode" -ForegroundColor Blue
    }
    
    Show-SuccessConfirm "One-Click Diagnose completed!"
}

function Start-EdgeCleanupTool {
    Clear-Host
    Write-Host "Starting Edge Cleanup Tool..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Gray
    
    $yuanbaoRunning, $yuanbaoPid = Test-YuanBaoRunning
    
    if ($yuanbaoRunning) {
        Write-Host "WARNING: Yuanbao is running (PID: $yuanbaoPid)" -ForegroundColor Yellow
        Write-Host "Cleanup may affect Yuanbao, recommend closing Yuanbao first" -ForegroundColor Yellow
    }
    
    Write-Host "`nThis will clean high memory Edge processes"
    Write-Host "Note: This may close Edge browser tabs"
    Write-Host ""
    Write-Host "Continue? (Y/N)" -ForegroundColor White
    
    $choice = Read-Host
    if ($choice -ne "Y" -and $choice -ne "y") {
        Write-Host "`nCleanup cancelled" -ForegroundColor Yellow
        Pause-Wait
        return
    }
    
    $edgeProcesses = Get-Process -Name "msedge" -ErrorAction SilentlyContinue
    
    if (-not $edgeProcesses) {
        Write-Host "No Edge processes found" -ForegroundColor Green
        Pause-Wait
        return
    }
    
    Write-Host "`nFound $($edgeProcesses.Count) Edge processes:" -ForegroundColor Green
    
    $highMemProcesses = @()
    $totalMem = 0
    
    foreach ($proc in $edgeProcesses) {
        $mem = [math]::Round($proc.WorkingSet64 / 1MB, 1)
        $totalMem += $mem
        
        $processInfo = @{
            Id = $proc.Id
            Memory = $mem
            Title = if ($proc.MainWindowTitle) { $proc.MainWindowTitle } else { "No Window" }
        }
        
        if ($mem -gt 500) {
            $highMemProcesses += $processInfo
        }
    }
    
    if ($highMemProcesses.Count -gt 0) {
        Write-Host "`nHigh Memory Edge Processes (>500MB):" -ForegroundColor Yellow
        foreach ($proc in $highMemProcesses) {
            Write-Host "  - PID $($proc.Id): $($proc.Memory) MB [$($proc.Title)]" -ForegroundColor Red
        }
    } else {
        Write-Host "`nNo high memory Edge processes" -ForegroundColor Green
    }
    
    Write-Host "`nTotal Memory: ${totalMem} MB" -ForegroundColor Gray
    
    if ($highMemProcesses.Count -gt 0) {
        Write-Host "`nConfirm cleanup? (Enter CLEAN to confirm)" -ForegroundColor White
        Write-Host "This will close $($highMemProcesses.Count) processes" -ForegroundColor Red
        
        $confirm = Read-Host
        if ($confirm -eq "CLEAN") {
            $cleaned = 0
            foreach ($proc in $highMemProcesses) {
                try {
                    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                    Write-Host "  CLEANED: PID $($proc.Id)" -ForegroundColor Green
                    $cleaned++
                } catch {
                    Write-Host "  FAILED: PID $($proc.Id)" -ForegroundColor Red
                }
            }
            $resultMsg = "Cleanup completed: $cleaned/$($highMemProcesses.Count) processes"
        } else {
            $resultMsg = "Cleanup cancelled"
            Write-Host "`nCleanup cancelled" -ForegroundColor Yellow
        }
    } else {
        $resultMsg = "No cleanup needed"
    }
    
    Show-SuccessConfirm $resultMsg
}

function Main {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Yuanbao Safe Memory Manager v3.0" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Safe Mode - Won't terminate Yuanbao" -ForegroundColor Green
    Write-Host "  Version: Fixed Edition" -ForegroundColor Gray
    Write-Host "  Date: $(Get-Date -Format 'yyyy-MM-dd')" -ForegroundColor Gray
    Write-Host "========================================" -ForegroundColor Cyan
    
    Start-Sleep -Seconds 1
    
    do {
        $choice = Show-MainMenu
        
        switch ($choice) {
            "1" { Start-SystemStatusCheck }
            "2" { Start-SafeCleanup }
            "3" { Start-SafeMonitor }
            "4" { Start-SystemRepair }
            "5" { Start-SystemDiagnose }
            "6" { Start-EdgeCleanupTool }
            "0" { 
                Write-Host "`nThank you for using, goodbye!" -ForegroundColor Green
                Start-Sleep -Seconds 2
                exit 0
            }
            default {
                Write-Host "`nInvalid option, please try again" -ForegroundColor Red
                Start-Sleep -Seconds 1
            }
        }
    } while ($true)
}

try {
    Main
} catch {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "  ERROR" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
