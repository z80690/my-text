# WebView2 内存泄漏解决方案

## 问题分析

### 问题描述
- WebView2 是 Microsoft Edge 浏览器和许多应用程序（如"元宝"应用）底层使用的嵌入式浏览器组件
- 系统兼容性问题导致内存泄漏
- 多进程架构导致资源占用过高

### 根本原因
1. **运行时版本不兼容**：WebView2 Runtime 版本与系统或应用程序不匹配
2. **进程隔离问题**：每个 WebView2 实例创建独立进程，未正确清理
3. **缓存累积**：WebView2 的缓存机制未正确管理
4. **内存回收延迟**：JavaScript 垃圾回收与原生代码交互问题

---

## 解决方案

### 步骤一：检查并更新 WebView2 Runtime

```powershell
# 检查已安装的 WebView2 版本
Get-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" -ErrorAction SilentlyContinue

# 检查 WebView2 安装目录
Get-ChildItem -Path "C:\Program Files (x86)\Microsoft\EdgeWebView2" -ErrorAction SilentlyContinue
```

### 步骤二：下载并安装最新 WebView2 Runtime

**离线安装包下载地址**：
- **稳定版**：https://go.microsoft.com/fwlink/p/?LinkId=2124703
- **固定版本**：https://developer.microsoft.com/en-us/microsoft-edge/webview2/#download-section

**安装命令**：
```powershell
# 静默安装 WebView2 Runtime
.\MicrosoftEdgeWebView2RuntimeInstallerX64.exe /silent /install
```

### 步骤三：配置 WebView2 运行时参数

创建配置文件 `WebView2Config.reg`：

```reg
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Microsoft\Edge\WebView2]
"AdditionalBrowserArguments"="--disable-gpu --disable-software-rasterizer --max-old-space-size=512"
"DefaultBrowserFolderPath"="C:\\Program Files (x86)\\Microsoft\\EdgeWebView2\\Application"
"UserDataFolder"="C:\\Users\\%USERNAME%\\AppData\\Local\\WebView2\\UserData"

[HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Edge\WebView2]
"IsWebView2RuntimeEnabled"=dword:00000001
"DisableWebView2"=dword:00000000
```

**应用配置**：
```powershell
reg import WebView2Config.reg
```

### 步骤四：创建内存监控脚本

创建 `WebView2Monitor.ps1`：

```powershell
<#
.SYNOPSIS
监控 WebView2 进程内存使用并自动清理

.DESCRIPTION
定期检查 WebView2 进程，当内存超过阈值时自动重启进程
#>

param(
    [int]$MemoryThresholdMB = 500,
    [int]$CheckIntervalSeconds = 60,
    [int]$MaxProcessAgeMinutes = 60
)

Write-Host "WebView2 内存监控脚本启动"
Write-Host "内存阈值: $MemoryThresholdMB MB"
Write-Host "检查间隔: $CheckIntervalSeconds 秒"
Write-Host "最大进程年龄: $MaxProcessAgeMinutes 分钟"

while ($true) {
    $webviewProcesses = Get-Process msedgewebview2 -ErrorAction SilentlyContinue
    
    foreach ($process in $webviewProcesses) {
        $memoryMB = [math]::Round($process.WorkingSet / 1MB, 2)
        $ageMinutes = [math]::Round((Get-Date - $process.StartTime).TotalMinutes, 2)
        
        Write-Host "$(Get-Date): 进程ID: $($process.Id), 内存: ${memoryMB}MB, 运行时间: ${ageMinutes}分钟"
        
        # 内存超过阈值时终止进程
        if ($memoryMB -gt $MemoryThresholdMB) {
            Write-Host "警告: 进程 $($process.Id) 内存超过阈值，正在终止..."
            $process | Stop-Process -Force -ErrorAction SilentlyContinue
        }
        
        # 进程运行时间过长时终止
        if ($ageMinutes -gt $MaxProcessAgeMinutes) {
            Write-Host "警告: 进程 $($process.Id) 运行时间过长，正在终止..."
            $process | Stop-Process -Force -ErrorAction SilentlyContinue
        }
    }
    
    Start-Sleep -Seconds $CheckIntervalSeconds
}
```

**使用方法**：
```powershell
# 启动监控（内存阈值 500MB，每分钟检查一次）
.\WebView2Monitor.ps1 -MemoryThresholdMB 500 -CheckIntervalSeconds 60

# 后台运行
Start-Job -ScriptBlock { .\WebView2Monitor.ps1 }
```

### 步骤五：创建定时清理任务

```powershell
# 创建定时任务：每天凌晨3点清理 WebView2 缓存
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Command ""Remove-Item -Path 'C:\Users\%USERNAME%\AppData\Local\WebView2\*' -Recurse -Force -ErrorAction SilentlyContinue"""

$trigger = New-ScheduledTaskTrigger -Daily -At 3:00AM

$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount

Register-ScheduledTask -TaskName "CleanWebView2Cache" -Action $action -Trigger $trigger -Principal $principal
```

### 步骤六：为元宝应用创建专用配置

创建 `yuanbao_webview2_fix.bat`：

```bat
@echo off
echo 修复元宝应用 WebView2 内存泄漏问题...

:: 终止现有的 WebView2 进程
taskkill /F /IM msedgewebview2.exe 2>NUL

:: 设置 WebView2 环境变量
set WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--disable-gpu --disable-software-rasterizer --max-old-space-size=256
set WEBVIEW2_USER_DATA_FOLDER=%LOCALAPPDATA%\WebView2\YuanBao

:: 启动元宝应用
start "" "C:\Path\To\YuanBao.exe"

echo 修复完成！
```

---

## 验证测试

### 测试步骤

1. **启动测试**
```powershell
# 启动监控脚本
Start-Job -ScriptBlock { .\WebView2Monitor.ps1 -MemoryThresholdMB 500 -CheckIntervalSeconds 30 }

# 启动元宝应用
.\yuanbao_webview2_fix.bat
```

2. **监控内存使用**
```powershell
# 实时监控内存
while ($true) {
    Get-Process msedgewebview2 -ErrorAction SilentlyContinue | Select-Object Id, Name, @{Name='MemoryMB';Expression={[math]::Round($_.WorkingSet/1MB,2)}}, StartTime
    Start-Sleep -Seconds 10
}
```

3. **验证修复效果**
```powershell
# 检查是否有内存持续增长
# 预期结果：内存稳定在阈值以下，进程定期被清理

# 检查任务计划是否创建成功
Get-ScheduledTask -TaskName "CleanWebView2Cache"
```

### 成功标准

| 指标 | 成功标准 |
|------|----------|
| 内存稳定 | WebView2 进程内存 ≤ 500MB |
| 进程重启 | 超过阈值时自动重启 |
| 缓存清理 | 定时任务正常执行 |
| 系统负载 | 整体 CPU 使用率下降 |

---

## 预防措施

1. **定期更新 WebView2 Runtime**
```powershell
# 每月检查更新
winget upgrade Microsoft.WebView2Runtime
```

2. **限制 WebView2 进程数量**
- 在应用程序中配置 `CoreWebView2EnvironmentOptions`
- 设置合理的进程池大小

3. **启用内存监控告警**
```powershell
# 创建性能计数器告警
New-EventLog -LogName Application -Source "WebView2Monitor"

# 在监控脚本中添加告警逻辑
Write-EventLog -LogName Application -Source "WebView2Monitor" -EventId 1001 -EntryType Warning -Message "WebView2 内存超过阈值"
```

---

## 紧急恢复

如果问题持续存在，执行以下步骤：

```powershell
# 1. 终止所有 WebView2 相关进程
taskkill /F /IM msedgewebview2.exe /T
taskkill /F /IM msedge.exe /T

# 2. 清理缓存
Remove-Item -Path "$env:LOCALAPPDATA\WebView2\*" -Recurse -Force

# 3. 重新安装 WebView2 Runtime
winget install Microsoft.WebView2Runtime --force

# 4. 重启系统
Restart-Computer -Force
```

---

## 版本信息

| 项目 | 版本 |
|------|------|
| WebView2 Runtime | 124.0.2478.67 (推荐) |
| 解决方案版本 | v1.0 |
| 创建日期 | 2026-05-11 |
