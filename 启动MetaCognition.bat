@echo off
chcp 65001 >nul
title Meta-Cognition 守护进程 - 完全自动模式
echo ================================================================================
echo  Meta-Cognition 守护进程启动器
echo  数据存储: %~dp0meta-cognition-data\
echo ================================================================================
echo.

cd /d "%~dp0"

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo [启动] Meta-Cognition 守护进程...
echo.

python meta-cognition-manager.py

echo.
echo [完成] 守护进程已停止
pause
