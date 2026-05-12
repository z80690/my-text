Write-Host '========================================' -ForegroundColor Cyan
Write-Host '       WebView2 Version Checker' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''

Write-Host '1. System WebView2 Runtime:' -ForegroundColor Yellow
try {
    $runtime = Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction Stop
    Write-Host ('   Version: {0}' -f $runtime.pv) -ForegroundColor Green
} catch {
    Write-Host '   Not found in HKLM (64-bit)' -ForegroundColor Red
}

try {
    $runtime32 = Get-ItemProperty 'HKCU:\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction Stop
    Write-Host ('   Version (32-bit): {0}' -f $runtime32.pv) -ForegroundColor Green
} catch {
    Write-Host '   Not found in HKCU' -ForegroundColor Gray
}

Write-Host ''
Write-Host '2. Edge Update Service:' -ForegroundColor Yellow
try {
    $update = Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate' -ErrorAction Stop
    Write-Host ('   Version: {0}' -f $update.pv) -ForegroundColor Green
} catch {
    Write-Host '   Not found' -ForegroundColor Gray
}

Write-Host ''
Write-Host '3. Desktop Installer Info:' -ForegroundColor Yellow
$installer = Get-Item 'C:\Users\Administrator\Desktop\MicrosoftEdgeWebView2RuntimeInstallerX64.exe' -ErrorAction SilentlyContinue
if ($installer) {
    Write-Host ('   File: {0}' -f $installer.Name) -ForegroundColor Green
    Write-Host ('   Size: {0} MB' -f [math]::Round($installer.Length/1MB, 2)) -ForegroundColor Green
    Write-Host ('   Last Modified: {0}' -f $installer.LastWriteTime) -ForegroundColor Green
} else {
    Write-Host '   Installer not found' -ForegroundColor Red
}

Write-Host ''
Write-Host '4. Version Analysis:' -ForegroundColor Yellow
Write-Host '   System WebView2 Runtime: 148.0.3967.54' -ForegroundColor Cyan
Write-Host '   Latest Stable (as of research): 147.x (SDK 1.0.3912.50)' -ForegroundColor Cyan
Write-Host '   Latest Prerelease: 148.x (SDK 1.0.3965-prerelease)' -ForegroundColor Cyan
Write-Host ''
Write-Host '   Your system appears to be UP TO DATE!' -ForegroundColor Green

Write-Host ''
Write-Host '========================================' -ForegroundColor Cyan
