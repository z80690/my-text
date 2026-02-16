# ============================================================
# 知识图谱数据库目录整理脚本
# Knowledge Graph Database Directory Organization Script
# 
# 用途：整理混在 database/ 目录下的多个项目SQL文件
# 执行方式：在 PowerShell 中运行此脚本
# ============================================================

$ErrorActionPreference = "Stop"

# 定义路径
$basePath = "C:\Users\Administrator\Desktop\my-text\knowledge_graph_project\database"
$dbPath = $basePath

# 目标目录
$knowledgeGraphPath = "$dbPath\knowledge_graph"
$supabaseCheckPath = "$dbPath\supabase_check"
$archivePath = "$dbPath\archive"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "知识图谱数据库目录整理脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: 清理错误创建的子目录
Write-Host "[1/4] 清理错误创建的子目录..." -ForegroundColor Yellow

$cleanupDirs = @($knowledgeGraphPath, $supabaseCheckPath)
foreach ($dir in $cleanupDirs) {
    if (Test-Path $dir) {
        # 移动文件回根目录
        $files = Get-ChildItem $dir -File
        foreach ($file in $files) {
            $dest = Join-Path $dbPath $file.Name
            if (Test-Path $dest) {
                Write-Host "  ⚠️  冲突: $file.Name 已存在，跳过" -ForegroundColor DarkGray
            } else {
                Move-Item $file.FullName $dbPath -ErrorAction SilentlyContinue
                Write-Host "  ✓ 移动: $($file.Name)" -ForegroundColor Green
            }
        }
        # 删除空目录
        Remove-Item $dir -ErrorAction SilentlyContinue
        Write-Host "  ✓ 已删除: $(Split-Path $dir -Leaf)" -ForegroundColor Green
    }
}

Write-Host ""

# Step 2: 创建归档目录
Write-Host "[2/4] 创建归档目录..." -ForegroundColor Yellow
if (-not (Test-Path $archivePath)) {
    New-Item -ItemType Directory -Path $archivePath -Force | Out-Null
    Write-Host "  ✓ 创建: archive" -ForegroundColor Green
}

Write-Host ""

# Step 3: 移动其他项目文件到归档目录
Write-Host "[3/4] 识别并归档其他项目文件..." -ForegroundColor Yellow

# 识别非知识图谱项目的文件
$otherProjectFiles = @(
    "test_connectivity.py",
    "test_database_schema.py", 
    "test_auth_system.py",
    "test_roles_and_permissions.py",
    "test_zhipu_ai.py",
    "quickstart.py",
    "test_fixes.py"
)

foreach ($fileName in $otherProjectFiles) {
    $filePath = Join-Path $dbPath $fileName
    if (Test-Path $filePath) {
        $dest = Join-Path $archivePath $fileName
        Move-Item $filePath $dest -ErrorAction SilentlyContinue
        Write-Host "  ✓ 归档: $fileName" -ForegroundColor Green
    }
}

Write-Host ""

# Step 4: 验证最终结构
Write-Host "[4/4] 最终目录结构:" -ForegroundColor Yellow
Write-Host ""

$treeOutput = @"
database/
├── models.py                 ← Python模型文件（保留）
├── __init__.py               ← Python包初始化
├── schema.sql                ← 完整Schema
├── schema_basic.sql          ← 基础Schema
├── schema_minimal.sql        ← 最小化Schema
├── schema_v1.sql             ← v1版Schema
├── knowledge_graph_supabase_schema.sql
└── README.md                 ← 文档
"
Write-Host $treeOutput -ForegroundColor White

Write-Host ""
Write-Host "✅ 目录整理完成!" -ForegroundColor Green
Write-Host ""
Write-Host "当前文件列表:" -ForegroundColor Cyan
Get-ChildItem $dbPath -File | Select-Object Name | Format-Table -HideTableHeaders
