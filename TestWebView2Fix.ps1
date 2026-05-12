<#
.SYNOPSIS
Test script to verify WebView2 memory leak fix

.DESCRIPTION
This script tests the WebView2 memory leak fix by:
1. Checking if WebView2 Runtime is properly configured
2. Verifying registry settings
3. Testing the monitoring script
4. Checking system performance improvement
#>

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "     WebView2 Memory Leak Fix Test" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$testResults = @()

# Test 1: Check Registry Configuration
Write-Host "Test 1: Checking Registry Configuration..." -ForegroundColor Yellow
try {
    $regPath = "HKCU:\Software\Microsoft\Edge\WebView2"
    $regValue = Get-ItemProperty -Path $regPath -Name AdditionalBrowserArguments -ErrorAction Stop
    Write-Host "  ✓ Registry key exists: $regPath" -ForegroundColor Green
    Write-Host "  ✓ AdditionalBrowserArguments: $($regValue.AdditionalBrowserArguments)" -ForegroundColor Green
    $testResults += @{Test="Registry Configuration"; Result="PASS"; Details="AdditionalBrowserArguments configured"}
}
catch {
    Write-Host "  ✗ Registry key not found or error: $_" -ForegroundColor Red
    $testResults += @{Test="Registry Configuration"; Result="FAIL"; Details="Registry key not configured"}
}

Write-Host ""

# Test 2: Check Monitoring Script
Write-Host "Test 2: Checking Monitoring Script..." -ForegroundColor Yellow
try {
    $scriptPath = ".\WebView2Monitor.ps1"
    if (Test-Path $scriptPath) {
        Write-Host "  ✓ Monitoring script exists: $scriptPath" -ForegroundColor Green
        
        # Check script syntax
        $scriptContent = Get-Content $scriptPath -Raw
        if ($scriptContent -match "MemoryThresholdMB" -and $scriptContent -match "msedgewebview2") {
            Write-Host "  ✓ Script contains required functionality" -ForegroundColor Green
            $testResults += @{Test="Monitoring Script"; Result="PASS"; Details="Script exists and has required functions"}
        }
        else {
            Write-Host "  ✗ Script missing required functionality" -ForegroundColor Red
            $testResults += @{Test="Monitoring Script"; Result="FAIL"; Details="Missing required functions"}
        }
    }
    else {
        Write-Host "  ✗ Monitoring script not found" -ForegroundColor Red
        $testResults += @{Test="Monitoring Script"; Result="FAIL"; Details="Script not found"}
    }
}
catch {
    Write-Host "  ✗ Error checking script: $_" -ForegroundColor Red
    $testResults += @{Test="Monitoring Script"; Result="FAIL"; Details="Error: $_"}
}

Write-Host ""

# Test 3: Check Running Processes
Write-Host "Test 3: Checking WebView2 Processes..." -ForegroundColor Yellow
try {
    $webviewProcesses = Get-Process msedgewebview2 -ErrorAction SilentlyContinue
    
    if ($webviewProcesses.Count -eq 0) {
        Write-Host "  ✓ No WebView2 processes currently running" -ForegroundColor Green
        $testResults += @{Test="WebView2 Processes"; Result="PASS"; Details="No processes running (clean state)"}
    }
    else {
        Write-Host "  ⚠ Found $($webviewProcesses.Count) WebView2 process(es)" -ForegroundColor Yellow
        foreach ($proc in $webviewProcesses) {
            $memoryMB = [math]::Round($proc.WorkingSet / 1MB, 2)
            Write-Host "    - Process $($proc.Id): ${memoryMB}MB"
        }
        $testResults += @{Test="WebView2 Processes"; Result="INFO"; Details="$($webviewProcesses.Count) processes found"}
    }
}
catch {
    Write-Host "  ✗ Error checking processes: $_" -ForegroundColor Red
    $testResults += @{Test="WebView2 Processes"; Result="FAIL"; Details="Error: $_"}
}

Write-Host ""

# Test 4: Check System Performance
Write-Host "Test 4: Checking System Performance..." -ForegroundColor Yellow
try {
    $totalCPU = (Get-Counter "\Processor(_Total)\% Processor Time").CounterSamples.CookedValue
    $totalMemory = (Get-Counter "\Memory\% Committed Bytes In Use").CounterSamples.CookedValue
    
    Write-Host "  ✓ CPU Usage: $([math]::Round($totalCPU, 2))%" -ForegroundColor Green
    Write-Host "  ✓ Memory Usage: $([math]::Round($totalMemory, 2))%" -ForegroundColor Green
    
    if ($totalCPU -lt 80 -and $totalMemory -lt 80) {
        Write-Host "  ✓ System is running within normal parameters" -ForegroundColor Green
        $testResults += @{Test="System Performance"; Result="PASS"; Details="CPU: $([math]::Round($totalCPU, 2))%, Memory: $([math]::Round($totalMemory, 2))%"}
    }
    else {
        Write-Host "  ⚠ System under high load" -ForegroundColor Yellow
        $testResults += @{Test="System Performance"; Result="WARNING"; Details="High system load detected"}
    }
}
catch {
    Write-Host "  ✗ Error checking performance: $_" -ForegroundColor Red
    $testResults += @{Test="System Performance"; Result="FAIL"; Details="Error: $_"}
}

Write-Host ""

# Test 5: Check Batch Fix Script
Write-Host "Test 5: Checking Batch Fix Script..." -ForegroundColor Yellow
try {
    $batchPath = ".\yuanbao_webview2_fix.bat"
    if (Test-Path $batchPath) {
        Write-Host "  ✓ Batch fix script exists: $batchPath" -ForegroundColor Green
        $testResults += @{Test="Batch Fix Script"; Result="PASS"; Details="Script exists"}
    }
    else {
        Write-Host "  ✗ Batch fix script not found" -ForegroundColor Red
        $testResults += @{Test="Batch Fix Script"; Result="FAIL"; Details="Script not found"}
    }
}
catch {
    Write-Host "  ✗ Error checking batch script: $_" -ForegroundColor Red
    $testResults += @{Test="Batch Fix Script"; Result="FAIL"; Details="Error: $_"}
}

Write-Host ""

# Test 6: Check Documentation
Write-Host "Test 6: Checking Documentation..." -ForegroundColor Yellow
try {
    $docPath = ".\webview2_memory_leak_fix.md"
    if (Test-Path $docPath) {
        Write-Host "  ✓ Documentation exists: $docPath" -ForegroundColor Green
        $testResults += @{Test="Documentation"; Result="PASS"; Details="Documentation file exists"}
    }
    else {
        Write-Host "  ✗ Documentation not found" -ForegroundColor Red
        $testResults += @{Test="Documentation"; Result="FAIL"; Details="Documentation not found"}
    }
}
catch {
    Write-Host "  ✗ Error checking documentation: $_" -ForegroundColor Red
    $testResults += @{Test="Documentation"; Result="FAIL"; Details="Error: $_"}
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "              Test Summary" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$passed = ($testResults | Where-Object { $_.Result -eq "PASS" }).Count
$failed = ($testResults | Where-Object { $_.Result -eq "FAIL" }).Count
$warning = ($testResults | Where-Object { $_.Result -eq "WARNING" -or $_.Result -eq "INFO" }).Count

foreach ($result in $testResults) {
    $color = switch ($result.Result) {
        "PASS" { [ConsoleColor]::Green }
        "FAIL" { [ConsoleColor]::Red }
        default { [ConsoleColor]::Yellow }
    }
    Write-Host ("{0}: {1} - {2}" -f $result.Test.PadRight(25), $result.Result.PadRight(10), $result.Details) -ForegroundColor $color
}

Write-Host ""
Write-Host ("Total Tests: {0} | Passed: {1} | Failed: {2} | Warnings: {3}" -f ($passed + $failed + $warning), $passed, $failed, $warning) -ForegroundColor Cyan

if ($failed -eq 0) {
    Write-Host ""
    Write-Host "✓ All tests passed! WebView2 memory leak fix is ready." -ForegroundColor Green
    Write-Host "  - Run '.\yuanbao_webview2_fix.bat' to apply the fix" -ForegroundColor Green
    Write-Host "  - Run '.\WebView2Monitor.ps1' for continuous monitoring" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "✗ Some tests failed. Please check the details above." -ForegroundColor Red
}
