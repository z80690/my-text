<#
.SYNOPSIS
WebView2 Memory Monitor - READ ONLY VERSION

.DESCRIPTION
Monitors WebView2 processes WITHOUT terminating them.
Only reports status and alerts - does NOT affect running applications.
#>

param(
    [int]$WarningThresholdMB = 800,
    [int]$CriticalThresholdMB = 1000,
    [int]$CheckIntervalMinutes = 30
)

$CheckIntervalSeconds = $CheckIntervalMinutes * 60

$clockJob = Start-Job -ScriptBlock {
    while ($true) {
        Get-Date
        Start-Sleep -Milliseconds 1000
    }
}

function Get-RealTime {
    $jobResult = Receive-Job -Name $clockJob.Name -Keep -ErrorAction SilentlyContinue
    if ($jobResult) {
        return $jobResult[-1]
    }
    return Get-Date
}

function Get-CPUUsage {
    try {
        $cpu = (Get-Counter "\Processor(_Total)\% Processor Time" -ErrorAction Stop).CounterSamples.CookedValue
        return [math]::Round($cpu, 2)
    }
    catch {
        return 0
    }
}

function Get-MemoryUsage {
    try {
        $memory = (Get-Counter "\Memory\% Committed Bytes In Use" -ErrorAction Stop).CounterSamples.CookedValue
        return [math]::Round($memory, 2)
    }
    catch {
        return 0
    }
}

function Show-Header {
    Clear-Host
    $currentTime = Get-RealTime
    $cpu = Get-CPUUsage
    $memory = Get-MemoryUsage

    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host "        WebView2 Memory Monitor - READ ONLY (NO TERMINATION)" -ForegroundColor Cyan
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host (" System Time: {0}" -f $currentTime.ToString('yyyy-MM-dd HH:mm:ss')) -ForegroundColor Green
    Write-Host (" CPU Usage: {0}% | Memory Usage: {1}%" -f $cpu, $memory) -ForegroundColor Yellow
    Write-Host (" Warning: {0}MB | Critical: {1}MB | Check Interval: {2} minutes" -f $WarningThresholdMB, $CriticalThresholdMB, $CheckIntervalMinutes) -ForegroundColor Gray
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host " *** IMPORTANT: This monitor only REPORTS - it NEVER kills processes ***" -ForegroundColor Magenta
    Write-Host ""
}

function Show-ProcessInfo($process) {
    $memoryMB = [math]::Round($process.WorkingSet / 1MB, 2)
    $ageMinutes = [math]::Round((Get-Date).Subtract($process.StartTime).TotalMinutes, 2)
    $cpuUsage = [math]::Round($process.CPU, 2)

    Write-Host "----------------------------------------------------------------------"
    Write-Host (" Process ID  : {0}" -f $process.Id)
    Write-Host (" Name        : {0}" -f $process.ProcessName)
    Write-Host (" CPU Time    : {0}s" -f $cpuUsage)
    Write-Host (" Memory      : {0}MB" -f $memoryMB)
    Write-Host (" Age         : {0}min" -f $ageMinutes)
    Write-Host (" Start Time  : {0}" -f $process.StartTime)

    if ($memoryMB -gt $CriticalThresholdMB) {
        Write-Host " STATUS      : CRITICAL - {0}MB exceeds {1}MB threshold" -f $memoryMB, $CriticalThresholdMB -ForegroundColor Red
    }
    elseif ($memoryMB -gt $WarningThresholdMB) {
        Write-Host " STATUS      : WARNING - {0}MB exceeds {1}MB threshold" -f $memoryMB, $WarningThresholdMB -ForegroundColor Yellow
    }
    else {
        Write-Host " STATUS      : OK" -ForegroundColor Green
    }

    Write-Host "----------------------------------------------------------------------"
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  WebView2 Memory Monitor - READ ONLY VERSION" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT CHANGES:" -ForegroundColor Yellow
Write-Host "  1. This monitor ONLY REPORTS - it NEVER kills processes" -ForegroundColor White
Write-Host "  2. No applications will be terminated or affected" -ForegroundColor White
Write-Host "  3. You can safely use all applications while monitoring" -ForegroundColor White
Write-Host ""
Write-Host "Thresholds:" -ForegroundColor Yellow
Write-Host ("  Warning:  {0}MB" -f $WarningThresholdMB) -ForegroundColor White
Write-Host ("  Critical: {0}MB" -f $CriticalThresholdMB) -ForegroundColor White
Write-Host ("  Check Interval: {0} minutes" -f $CheckIntervalMinutes) -ForegroundColor White
Write-Host ""
Write-Host "Starting monitoring..." -ForegroundColor Green
Start-Sleep -Seconds 2

while ($true) {
    Show-Header

    $webviewProcesses = Get-Process msedgewebview2 -ErrorAction SilentlyContinue

    if ($webviewProcesses.Count -eq 0) {
        Write-Host "----------------------------------------------------------------------"
        Write-Host " No WebView2 processes detected - System is clean" -ForegroundColor Green
        Write-Host "----------------------------------------------------------------------"
    }
    else {
        Write-Host "----------------------------------------------------------------------"
        Write-Host (" Found {0} WebView2 process(es)" -f $webviewProcesses.Count) -ForegroundColor Yellow
        Write-Host "----------------------------------------------------------------------"

        $totalMemoryMB = 0
        $criticalProcesses = 0
        $warningProcesses = 0

        foreach ($process in $webviewProcesses) {
            Show-ProcessInfo $process

            $memoryMB = [math]::Round($process.WorkingSet / 1MB, 2)
            $totalMemoryMB += $memoryMB

            if ($memoryMB -gt $CriticalThresholdMB) {
                $criticalProcesses++
            }
            elseif ($memoryMB -gt $WarningThresholdMB) {
                $warningProcesses++
            }

            Write-Host ""
        }

        Write-Host "======================================================================"
        Write-Host (" Total WebView2 Memory: {0}MB across {1} processes" -f $totalMemoryMB, $webviewProcesses.Count) -ForegroundColor Cyan

        if ($criticalProcesses -gt 0) {
            Write-Host (" CRITICAL: {0} processes exceeding {1}MB - Manual action may be needed" -f $criticalProcesses, $CriticalThresholdMB) -ForegroundColor Red
        }
        elseif ($warningProcesses -gt 0) {
            Write-Host (" WARNING: {0} processes exceeding {1}MB - Monitor closely" -f $warningProcesses, $WarningThresholdMB) -ForegroundColor Yellow
        }
        else {
            Write-Host " All processes within acceptable range" -ForegroundColor Green
        }
        Write-Host "======================================================================"
    }

    Write-Host ""
    Write-Host ("Monitoring... Next check in {0} minutes. Press Ctrl+C to stop." -f $CheckIntervalMinutes) -ForegroundColor Gray
    for ($i = $CheckIntervalSeconds; $i -gt 0; $i--) {
        $currentTime = Get-RealTime
        $remainingMinutes = [math]::Floor($i / 60)
        $remainingSeconds = $i % 60
        Write-Host ("`r{0} - Next check in {1}:{2:D2}..." -f $currentTime.ToString('HH:mm:ss'), $remainingMinutes, $remainingSeconds) -NoNewline -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
    Write-Host ""
}

$clockJob | Stop-Job | Remove-Job
