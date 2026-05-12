<#
.SYNOPSIS
WebView2 Memory Monitor with Real-time Clock

.DESCRIPTION
Monitors WebView2 processes with real-time clock display
#>

param(
    [int]$MemoryThresholdMB = 500,
    [int]$CheckIntervalMinutes = 30,
    [int]$MaxProcessAgeMinutes = 60
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
    
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host "              WebView2 Memory Monitor v2.0                    " -ForegroundColor Cyan
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host (" System Time: {0}" -f $currentTime.ToString('yyyy-MM-dd HH:mm:ss')) -ForegroundColor Green
    Write-Host (" CPU Usage: {0}% | Memory Usage: {1}%" -f $cpu, $memory) -ForegroundColor Yellow
    Write-Host (" Threshold: {0}MB | Check Interval: {1} minutes" -f $MemoryThresholdMB, $CheckIntervalMinutes) -ForegroundColor Gray
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Show-ProcessInfo($process) {
    $memoryMB = [math]::Round($process.WorkingSet / 1MB, 2)
    $ageMinutes = [math]::Round((Get-Date).Subtract($process.StartTime).TotalMinutes, 2)
    $cpuUsage = [math]::Round($process.CPU, 2)
    
    Write-Host "-------------------------------------------------------------"
    Write-Host (" Process ID  : {0}" -f $process.Id)
    Write-Host (" Name        : {0}" -f $process.ProcessName)
    Write-Host (" CPU Time    : {0}s" -f $cpuUsage)
    Write-Host (" Memory      : {0}MB" -f $memoryMB)
    Write-Host (" Age         : {0}min" -f $ageMinutes)
    Write-Host (" Start Time  : {0}" -f $process.StartTime)
    
    if ($memoryMB -gt $MemoryThresholdMB) {
        Write-Host " STATUS      : WARNING - MEMORY EXCEEDED" -ForegroundColor Yellow
    }
    elseif ($ageMinutes -gt $MaxProcessAgeMinutes) {
        Write-Host " STATUS      : WARNING - PROCESS TOO OLD" -ForegroundColor Yellow
    }
    else {
        Write-Host " STATUS      : OK" -ForegroundColor Green
    }
    
    Write-Host "-------------------------------------------------------------"
}

Write-Host "Initializing WebView2 Memory Monitor..." -ForegroundColor Green
Write-Host ("Check interval set to {0} minutes" -f $CheckIntervalMinutes) -ForegroundColor Gray

while ($true) {
    Show-Header
    
    $webviewProcesses = Get-Process msedgewebview2 -ErrorAction SilentlyContinue
    
    if ($webviewProcesses.Count -eq 0) {
        Write-Host "-------------------------------------------------------------"
        Write-Host " No WebView2 processes detected - System is clean" -ForegroundColor Gray
        Write-Host "-------------------------------------------------------------"
    }
    else {
        Write-Host "-------------------------------------------------------------"
        Write-Host (" Found {0} WebView2 process(es)" -f $webviewProcesses.Count) -ForegroundColor Yellow
        Write-Host "-------------------------------------------------------------"
        
        foreach ($process in $webviewProcesses) {
            Show-ProcessInfo $process
            
            $memoryMB = [math]::Round($process.WorkingSet / 1MB, 2)
            $ageMinutes = [math]::Round((Get-Date).Subtract($process.StartTime).TotalMinutes, 2)
            
            $shouldTerminate = $false
            
            if ($memoryMB -gt $MemoryThresholdMB) {
                Write-Host (" ACTION: Terminating process {0} - Memory exceeded {1}MB" -f $process.Id, $MemoryThresholdMB) -ForegroundColor Red
                $shouldTerminate = $true
            }
            
            if ($ageMinutes -gt $MaxProcessAgeMinutes) {
                Write-Host (" ACTION: Terminating process {0} - Age exceeded {1}min" -f $process.Id, $MaxProcessAgeMinutes) -ForegroundColor Red
                $shouldTerminate = $true
            }
            
            if ($shouldTerminate) {
                try {
                    $process | Stop-Process -Force -ErrorAction Stop
                    Write-Host (" RESULT: Successfully terminated process {0}" -f $process.Id) -ForegroundColor Green
                }
                catch {
                    Write-Host (" RESULT: Failed to terminate process {0}: {1}" -f $process.Id, $_) -ForegroundColor Red
                }
            }
            
            Write-Host ""
        }
    }
    
    Write-Host ("Next check in {0} minutes..." -f $CheckIntervalMinutes) -ForegroundColor Gray
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
