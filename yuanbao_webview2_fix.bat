@echo off
chcp 65001 >nul
echo ==============================================
echo      元宝应用 WebView2 内存泄漏修复工具
echo ==============================================
echo.

:: 检查是否以管理员身份运行
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo 请以管理员身份运行此脚本！
    pause
    exit /b 1
)

echo 步骤1: 终止现有的 WebView2 进程...
taskkill /F /IM msedgewebview2.exe 2>NUL
taskkill /F /IM msedge.exe /T 2>NUL
echo 完成！

echo.
echo 步骤2: 清理 WebView2 缓存...
rmdir /S /Q "%LOCALAPPDATA%\WebView2" 2>NUL
mkdir "%LOCALAPPDATA%\WebView2" 2>NUL
echo 完成！

echo.
echo 步骤3: 应用 WebView2 优化配置...
reg import WebView2Config.reg
echo 完成！

echo.
echo 步骤4: 配置环境变量...
setx WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS "--disable-gpu --disable-software-rasterizer --max-old-space-size=256"
setx WEBVIEW2_USER_DATA_FOLDER "%LOCALAPPDATA%\WebView2\YuanBao"
echo 完成！

echo.
echo ==============================================
echo           修复完成！
echo ==============================================
echo 建议：
echo 1. 重新启动元宝应用
echo 2. 运行 WebView2Monitor.ps1 进行实时监控
echo 3. 如果问题依旧，请更新 WebView2 Runtime
echo.
pause
