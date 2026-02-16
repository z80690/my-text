# ============================================================
# 数据库目录结构初始化脚本
# Database Directory Structure Setup Script
#
# 用途: 在项目database目录下创建标准化的目录结构
# 用法: 在 database/ 目录下执行此脚本
#
# 版本: 1.0.0
# 日期: 2026-01-20
# ============================================================

$ErrorActionPreference = "Stop"

# 获取脚本所在目录（database目录）
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "数据库目录结构初始化脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "项目根目录: $projectRoot" -ForegroundColor White
Write-Host "数据库目录: $scriptDir" -ForegroundColor White
Write-Host ""

# ============================================
# Step 1: 定义目录结构
# ============================================
Write-Host "[1/5] 定义目录结构..." -ForegroundColor Yellow

$directoryStructure = @{
    # 核心目录
    "schemas"              = "正式Schema定义（生产环境使用）"
    "migrations"           = "数据库迁移脚本（按版本排序）"
    "seeds"                = "种子数据（初始化基础数据）"
    "staging"              = "开发/测试用Schema（不稳定）"
    "archive"              = "已废弃的旧版本"
    
    # 辅助目录
    "views"                = "视图定义"
    "functions"            = "存储过程和函数"
    "triggers"             = "触发器定义"
    "indexes"              = "独立索引定义"
    "utilities"            = "工具脚本"
    "tests"                = "数据库测试"
    "docs"                 = "技术文档"
    "config"               = "环境配置"
    "logs"                 = "执行日志"
}

Write-Host "将创建以下目录:" -ForegroundColor White
foreach ($dir in $directoryStructure.Keys) {
    Write-Host "  • $dir/ - $($directoryStructure[$dir])" -ForegroundColor Gray
}
Write-Host ""

# ============================================
# Step 2: 创建目录
# ============================================
Write-Host "[2/5] 创建目录结构..." -ForegroundColor Yellow

$created = 0
$skipped = 0

foreach ($dir in $directoryStructure.Keys) {
    $fullPath = Join-Path $scriptDir $dir
    
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  ✓ 创建: $dir/" -ForegroundColor Green
        $created++
    } else {
        Write-Host "  ○ 跳过: $dir/ (已存在)" -ForegroundColor DarkGray
        $skipped++
    }
}

Write-Host "  → 新建: $created, 跳过: $skipped" -ForegroundColor White
Write-Host ""

# ============================================
# Step 3: 移动现有SQL文件
# ============================================
Write-Host "[3/5] 分类移动现有SQL文件..." -ForegroundColor Yellow

# 定义文件分类规则
$fileCategories = @{
    # schemas/ - 正式版本
    "schema.sql"                       = "schemas"
    "schema_v1.sql"                    = "schemas"
    "schema_v2.sql"                    = "schemas"
    
    # staging/ - 测试版本
    "schema_basic.sql"                 = "staging"
    "schema_minimal.sql"               = "staging"
    "schema_dev.sql"                   = "staging"
    
    # archive/ - 归档版本
    "knowledge_graph_supabase_schema.sql" = "archive"
    "legacy_schema.sql"                = "archive"
    "old_*.sql"                        = "archive"
}

$moved = 0
$conflicts = 0

# 获取所有SQL文件
$sqlFiles = Get-ChildItem $scriptDir -File -Filter "*.sql"

foreach ($file in $sqlFiles) {
    $destDir = $null
    
    # 精确匹配
    if ($fileCategories.ContainsKey($file.Name)) {
        $destDir = $fileCategories[$file.Name]
    }
    # 模式匹配
    else {
        foreach ($pattern in $fileCategories.Keys) {
            if ($pattern -like "old_*.sql" -and $file.Name -like "old_*.sql") {
                $destDir = $fileCategories[$pattern]
                break
            }
        }
    }
    
    if ($destDir) {
        $destPath = Join-Path $scriptDir $destDir $file.Name
        
        if (-not (Test-Path $destPath)) {
            Move-Item $file.FullName $destPath -ErrorAction SilentlyContinue
            Write-Host "  → $destDir/$($file.Name)" -ForegroundColor White
            $moved++
        } else {
            Write-Host "  ⚠️  冲突: $($file.Name) (目标已存在)" -ForegroundColor Yellow
            $conflicts++
        }
    }
}

Write-Host "  → 移动: $moved, 冲突: $conflicts" -ForegroundColor White
Write-Host ""

# ============================================
# Step 4: 创建示例文件
# ============================================
Write-Host "[4/5] 创建示例和模板文件..." -ForegroundColor Yellow

# 创建 .gitkeep
$gitkeepPath = Join-Path $scriptDir ".gitkeep"
if (-not (Test-Path $gitkeepPath)) {
    "# 数据库目录" | Out-File $gitkeepPath -Encoding UTF8
    Write-Host "  ✓ 创建: .gitkeep" -ForegroundColor Green
}

# 创建 schemas/CURRENT.sql.example
$currentExample = Join-Path $scriptDir "schemas\CURRENT.sql.example"
if (-not (Test-Path $currentExample)) {
    @"
-- 当前生产版本链接
-- 请根据实际版本修改
-- 例如: v1/schema.sql 或 v2/schema.sql

-- 方式1: 使用 \i 包含
-- \i schemas/v1/schema.sql

-- 方式2: 复制内容
-- 此文件用于在Supabase SQL编辑器中快速执行当前版本
"@ | Out-File $currentExample -Encoding UTF8
    Write-Host "  ✓ 创建: schemas/CURRENT.sql.example" -ForegroundColor Green
}

# 创建 seeds/README示例
$seedsReadme = Join-Path $scriptDir "seeds\README.md"
if (-not (Test-Path $seedsReadme)) {
    @"
# 种子数据

本目录包含数据库初始化所需的种子数据。

## 文件命名规则

- `NNN_name.sql` - NNN为3位数字序号

## 执行顺序

1. `001_platforms.sql` - 平台数据
2. `002_categories.sql` - 分类数据
3. ...

## 添加新种子数据

1. 创建新的种子文件
2. 更新本README.md
3. 在部署时按序号执行
"@ | Out-File $seedsReadme -Encoding UTF8
    Write-Host "  ✓ 创建: seeds/README.md" -ForegroundColor Green
}

# 创建 migrations/README示例
$migrationsReadme = Join-Path $scriptDir "migrations\README.md"
if (-not (Test-Path $migrationsReadme)) {
    @"
# 数据库迁移

本目录包含数据库结构变更的迁移脚本。

## 命名规则

- `NNN_migration_name/` - 迁移目录
  - `up.sql` - 正向迁移（添加/修改）
  - `down.sql` - 逆向迁移（回滚）
  - `README.md` - 可选的迁移说明

## 执行迁移

```bash
# 执行所有pending迁移
psql -d database -f migrations/MIGRATIONS.md

# 执行单个迁移
psql -d database -f migrations/001_name/up.sql
```

## 创建新迁移

1. 创建目录: `mkdir migrations/003_new_feature`
2. 创建文件: `up.sql` 和 `down.sql`
3. 编写迁移内容
4. 更新 MIGRATIONS.md
"@ | Out-File $migrationsReadme -Encoding UTF8
    Write-Host "  ✓ 创建: migrations/README.md" -ForegroundColor Green
}

Write-Host ""

# ============================================
# Step 5: 显示最终目录树
# ============================================
Write-Host "[5/5] 最终目录结构:" -ForegroundColor Yellow
Write-Host ""

$tree = @"
database/
├── README.md                  ← 项目数据库说明
├── DIRECTORY_STRUCTURE.md     ← 本规范文档
├── .gitkeep                   ← Git占位符
│
├── schemas/                   ← 正式Schema（生产）
│   ├── schema.sql             ← 完整标准版
│   ├── schema_v1.sql          ← v1正式版
│   └── CURRENT.sql.example    ← 当前版本示例
│
├── migrations/                ← 版本迁移
│   └── README.md              ← 迁移说明
│
├── seeds/                     ← 种子数据
│   └── README.md              ← 种子说明
│
├── staging/                   ← 开发/测试
│   ├── schema_basic.sql       ← 基础简化版
│   └── schema_minimal.sql     ← 最简版
│
├── archive/                   ← 历史归档
│   └── knowledge_graph_supabase_schema.sql
│
├── views/                     ← 视图定义
├── functions/                 ← 存储过程
├── triggers/                  ← 触发器
├── indexes/                   ← 索引定义
├── utilities/                 ← 工具脚本
├── tests/                     ← 测试脚本
├── docs/                      ← 技术文档
├── config/                    ← 环境配置
└── logs/                      ← 执行日志
"@

Write-Host $tree -ForegroundColor White
Write-Host ""

# ============================================
# 统计信息
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "初始化完成!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$dirCount = (Get-ChildItem $scriptDir -Directory).Count
$fileCount = (Get-ChildItem $scriptDir -File -Recurse).Count

Write-Host "统计信息:" -ForegroundColor White
Write-Host "  • 目录总数: $dirCount" -ForegroundColor Gray
Write-Host "  • 文件总数: $fileCount" -ForegroundColor Gray
Write-Host ""

Write-Host "下一步操作:" -ForegroundColor White
Write-Host "  1. 阅读 DIRECTORY_STRUCTURE.md 了解规范" -ForegroundColor Gray
Write-Host "  2. 将现有Schema文件分类到对应目录" -ForegroundColor Gray
Write-Host "  3. 创建迁移脚本管理结构变更" -ForegroundColor Gray
Write-Host "  4. 更新项目README.md引用新结构" -ForegroundColor Gray
Write-Host ""

Write-Host "✅ 数据库目录结构初始化完成!" -ForegroundColor Green
