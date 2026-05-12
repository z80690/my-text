@echo off
setlocal

:: 设置 Node.js 路径
set PATH=C:\Users\Administrator\Desktop\my-text\.trae;%PATH%

:: 测试 Node.js
echo Testing Node.js...
node --version
if %errorlevel% equ 0 (
    echo Node.js is working!
) else (
    echo Node.js failed!
    pause
    exit /b 1
)

:: 测试 npx
echo Testing npx...
npx --version
if %errorlevel% equ 0 (
    echo npx is working!
) else (
    echo npx failed!
    pause
    exit /b 1
)

echo All tests passed!
pause