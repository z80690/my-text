@echo off
setlocal

echo 🚀 启动自动记忆MCP服务器...

:: 尝试不同的Python路径
set "PYTHON_PATHS=^
C:\ProgramData\Anaconda3\python.exe;^
C:\ProgramData\Anaconda3\envs\TraeAI-5\python.exe;^
C:\Users\Administrator\anaconda3\python.exe;^
C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe;^
python.exe"

for %%p in (%PYTHON_PATHS%) do (
    if exist "%%p" (
        echo 找到Python: %%p
        "%%p" ".trae/auto_memory_mcp.py"
        goto :end
    )
)

echo ❌ 找不到Python
pause

:end
endlocal
