# 拉尔夫循环 - 持续重试直到成功
Write-Host "🚀 启动拉尔夫循环..." -ForegroundColor Green

$pythonPaths = @(
    "C:\ProgramData\Anaconda3\python.exe",
    "C:\ProgramData\Anaconda3\envs\TraeAI-5\python.exe",
    "C:\Users\Administrator\anaconda3\python.exe",
    "C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"
)

$scriptPath = ".trae/auto_memory_mcp.py"
$maxRetries = 10

for ($attempt = 1; $attempt -le $maxRetries; $attempt++) {
    Write-Host "`n🔄 第 $attempt/$maxRetries 次尝试" -ForegroundColor Cyan
    
    foreach ($pythonPath in $pythonPaths) {
        if (Test-Path $pythonPath) {
            Write-Host "🔧 尝试使用Python: $pythonPath" -ForegroundColor Yellow
            
            $process = Start-Process -FilePath $pythonPath -ArgumentList $scriptPath -PassThru -NoNewWindow
            
            Start-Sleep -Seconds 3
            
            try {
                $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2
                $data = $response.Content | ConvertFrom-Json
                
                if ($data.status -eq "ok") {
                    Write-Host "✅ MCP服务启动成功！" -ForegroundColor Green
                    Write-Host "🔔 服务已在端口8000运行" -ForegroundColor Green
                    return
                }
            }
            catch {
                Write-Host "❌ 服务未响应" -ForegroundColor Red
            }
            
            $process.Kill()
        }
    }
    
    Write-Host "❌ 本次尝试失败，2秒后重试..." -ForegroundColor Red
    Start-Sleep -Seconds 2
}

Write-Host "`n❌ 达到最大重试次数，启动失败" -ForegroundColor Red
