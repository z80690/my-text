# 数据库目录结构规范

## Database Directory Structure Standard

**版本**: 1.0.0  
**创建日期**: 2026-01-20  
**适用项目**: 知识图谱数据库系统  
**数据库**: PostgreSQL / Supabase

---

## 1. 概述

### 1.1 规范目的

本规范旨在解决数据库相关文件杂乱存放的问题，建立一套标准化、可复用的目录结构，使团队成员能够快速定位文件、理解项目结构，并支持多环境部署。

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **职责分离** | 每个目录有明确的单一职责 |
| **版本管理** | 区分生产、测试、归档版本 |
| **环境隔离** | 支持 dev/staging/prod 环境分离 |
| **可复用性** | 规范独立于具体项目，可复制到新项目 |
| **自文档化** | 目录结构即文档，新成员可快速上手 |

---

## 2. 标准目录结构

### 2.1 完整结构

```
database/
│
├── README.md                  # 数据库架构说明文档（根目录）
│
├── schemas/                   # 正式Schema定义（生产环境使用）
│   ├── v1/
│   │   ├── 001_init.sql       # 初始表结构
│   │   ├── 002_indexes.sql    # 索引定义
│   │   └── README.md          # v1版本说明
│   │
│   ├── v2/
│   │   ├── 001_init.sql
│   │   ├── 002_alter_users.sql
│   │   └── README.md
│   │
│   └── CURRENT.sql            # 指向当前生产版本的符号链接
│
├── migrations/                # 数据迁移脚本（按版本排序）
│   ├── 001_add_user_embedding/
│   │   ├── up.sql             # 迁移脚本
│   │   ├── down.sql           # 回滚脚本
│   │   └── README.md          # 迁移说明
│   │
│   ├── 002_create_relations/
│   │   ├── up.sql
│   │   ├── down.sql
│   │   └── README.md
│   │
│   └── MIGRATIONS.md          # 迁移日志汇总
│
├── seeds/                     # 种子数据（初始化数据）
│   ├── platforms/             # 平台种子数据
│   │   ├── 001_platforms.sql
│   │   └── README.md
│   │
│   ├── categories/            # 分类种子数据
│   │   ├── 001_categories.sql
│   │   └── README.md
│   │
│   └── SEEDS.md               # 种子数据说明
│
├── staging/                   # 开发/测试用Schema（不稳定）
│   ├── schema_basic.sql       # 基础简化版（快速启动）
│   ├── schema_minimal.sql     # 最简版（仅核心表）
│   └── schema_dev.sql         # 开发增强版（含测试数据）
│
├── archive/                   # 已废弃的旧版本
│   ├── v0/
│   │   └── README.md          # 归档说明
│   │
│   └── knowledge_graph_supabase_schema.sql  # 初始版本（已过时）
│
├── views/                     # 视图定义
│   ├── user_relations.sql     # 用户关系视图
│   ├── content_stats.sql      # 内容统计视图
│   └── README.md
│
├── functions/                 # 存储过程和函数
│   ├── update_timestamp.sql   # 更新时间触发器
│   ├── add_user.sql           # 添加用户存储过程
│   └── README.md
│
├── triggers/                  # 触发器定义
│   ├── update_users_timestamp.sql
│   ├── update_contents_timestamp.sql
│   └── README.md
│
├── indexes/                   # 独立索引定义（便于维护）
│   ├── idx_users_username.sql
│   ├── idx_contents_view_count.sql
│   └── README.md
│
├── utilities/                 # 工具脚本
│   ├── setup_database.ps1     # 数据库初始化脚本
│   ├── backup_database.ps1    # 备份脚本
│   ├── restore_database.ps1   # 恢复脚本
│   ├── generate_report.sql    # 数据报告生成
│   └── README.md
│
├── tests/                     # 数据库测试
│   ├── test_schema.sql        # Schema测试
│   ├── test_constraints.sql   # 约束测试
│   ├── test_functions.sql     # 函数测试
│   └── README.md
│
├── docs/                      # 文档
│   ├── SCHEMA.md              # 表结构文档
│   ├── ERD.png                # 实体关系图
│   ├── DATA_TYPES.md          # 数据类型说明
│   └── README.md
│
├── config/                    # 配置
│   ├── environments/          # 环境配置
│   │   ├── development.sql    # 开发环境
│   │   ├── staging.sql        # 测试环境
│   │   └── production.sql     # 生产环境
│   │
│   └── README.md
│
├── logs/                      # 执行日志
│   ├── migration_20260120.log
│   └── README.md
│
├── .gitkeep                   # Git占位符
│
└── DIRECTORY_STRUCTURE.md     # 本规范文档
```

### 2.2 简化结构（小型项目）

```
database/
├── README.md
├── schemas/
│   └── schema.sql             # 完整Schema
├── staging/
│   └── schema_dev.sql         # 开发版
├── archive/
│   └── legacy_schema.sql      # 旧版本
├── seeds/
│   └── platforms.sql
├── utilities/
│   └── setup.ps1
└── DIRECTORY_STRUCTURE.md
```

---

## 3. 文件命名约定

### 3.1 Schema 文件

| 类型 | 命名模式 | 示例 | 说明 |
|------|----------|------|------|
| 完整版 | `schema.sql` | `schema.sql` | 生产环境标准版 |
| 基础版 | `schema_basic.sql` | `schema_basic.sql` | 简化版，含核心表 |
| 最简版 | `schema_minimal.sql` | `schema_minimal.sql` | 仅核心表 |
| 开发版 | `schema_dev.sql` | `schema_dev.sql` | 开发增强版 |
| 版本化 | `v{n}/init.sql` | `v1/001_init.sql` | 带版本号 |

### 3.2 迁移文件

| 类型 | 命名模式 | 示例 | 说明 |
|------|----------|------|------|
| 迁移 | `NNN_name/up.sql` | `001_add_embedding/up.sql` | 正向迁移 |
| 回滚 | `NNN_name/down.sql` | `001_add_embedding/down.sql` | 逆向迁移 |

**规则**:
- NNN = 3位数字序号（001, 002, ...）
- name = 迁移描述（英文、下划线分隔）
- 每个迁移必须包含 up.sql 和 down.sql

### 3.3 种子文件

| 类型 | 命名模式 | 示例 | 说明 |
|------|----------|------|------|
| 平台 | `NNN_entity.sql` | `001_platforms.sql` | 平台种子数据 |
| 分类 | `NNN_entity.sql` | `002_categories.sql` | 分类种子数据 |

### 3.4 工具脚本

| 类型 | 命名模式 | 示例 | 说明 |
|------|----------|------|------|
| PowerShell | `*.ps1` | `setup_database.ps1` | PowerShell脚本 |
| SQL | `*.sql` | `generate_report.sql` | SQL脚本 |
| Bash | `*.sh` | `backup_db.sh` | Bash脚本 |

---

## 4. 目录职责说明

### 4.1 核心目录

| 目录 | 职责 | 存放内容 |
|------|------|---------|
| `schemas/` | 正式Schema | 生产环境使用的DDL定义 |
| `migrations/` | 版本迁移 | 数据库结构变更脚本 |
| `seeds/` | 种子数据 | 初始化基础数据 |
| `staging/` | 开发测试 | 不稳定的开发版本 |
| `archive/` | 历史归档 | 已废弃的旧版本 |

### 4.2 辅助目录

| 目录 | 职责 | 存放内容 |
|------|------|---------|
| `views/` | 视图定义 | SELECT语句视图 |
| `functions/` | 存储过程 | PL/pgSQL函数 |
| `triggers/` | 触发器 | DML触发器定义 |
| `indexes/` | 索引定义 | 独立索引创建脚本 |
| `utilities/` | 工具脚本 | 运维、部署脚本 |
| `tests/` | 测试脚本 | 数据库单元测试 |
| `docs/` | 技术文档 | ERD、API文档 |
| `config/` | 环境配置 | 不同环境配置 |
| `logs/` | 执行日志 | 迁移、日志记录 |

---

## 5. 版本管理策略

### 5.1 版本命名规范

```
主版本.次版本.修订版本
   1        0        0
```

| 级别 | 变更类型 | 示例 |
|------|---------|------|
| 主版本 | 重大结构变更 | v1 → v2 |
| 次版本 | 新增功能 | v1.0 → v1.1 |
| 修订版本 | Bug修复 | v1.0 → v1.0.1 |

### 5.2 环境区分

```
开发环境 (Development)
  └─ 位置: schemas/dev/ 或 staging/
  └─ 特点: 完整功能 + 测试数据
  └─ 数据库: local_supabase_dev

测试环境 (Staging)
  └─ 位置: schemas/staging/
  └─ 特点: 接近生产环境
  └─ 数据库: staging_supabase

生产环境 (Production)
  └─ 位置: schemas/v1/, schemas/v2/
  └─ 特点: 稳定版本
  └─ 数据库: production_supabase
```

### 5.3 版本发布流程

```
1. 开发 → staging/
   └── 在staging目录开发和测试

2. 测试通过 → schemas/v{n}/
   └── 创建新版本目录，复制稳定版本

3. 生产部署 → schemas/CURRENT.sql
   └── 更新CURRENT.sql指向生产版本
```

---

## 6. 快速开始

### 6.1 初始化目录结构

在项目根目录执行：

```powershell
# 方式1: 使用初始化脚本
cd database
.\utilities\setup_database_structure.ps1

# 方式2: 手动创建
mkdir schemas, migrations, seeds, staging, archive
mkdir views, functions, triggers, indexes
mkdir utilities, tests, docs, config, logs
```

### 6.2 添加新的迁移

```powershell
# 1. 创建迁移目录
mkdir database/migrations/003_new_feature

# 2. 创建迁移脚本
New-Item database/migrations/003_new_feature/up.sql
New-Item database/migrations/003_new_feature/down.sql

# 3. 编写迁移内容
# up.sql: 添加新表/字段
# down.sql: 回滚操作
```

### 6.3 添加种子数据

```powershell
# 1. 创建种子文件
New-Item database/seeds/003_new_data.sql

# 2. 编写种子数据
# INSERT INTO ... VALUES (...)
```

---

## 7. 最佳实践

### 7.1 文件组织

✅ **推荐做法**:
- 每个文件只做一件事
- 使用自描述的文件名
- 保持目录结构扁平（最多2层）
- 为复杂迁移添加README.md

❌ **避免做法**:
- 混合不同类型的文件
- 使用模糊的文件名（如 `test.sql`）
- 嵌套过深的目录
- 缺少文档的迁移

### 7.2 版本控制

✅ **推荐做法**:
- 所有SQL文件纳入Git版本控制
- 使用有意义的迁移序号
- 每个迁移包含回滚脚本
- 定期归档旧版本

❌ **避免做法**:
- 直接在生产库修改结构
- 跳过迁移步骤
- 使用自动生成的无意义序号

### 7.3 命名规范

✅ **推荐做法**:
```sql
-- 文件名：001_create_users_table.sql
-- 表名：users
-- 字段名：user_id, created_at
-- 索引名：idx_users_email
```

❌ **避免做法**:
```sql
-- 文件名：test1.sql
-- 表名：Table1
-- 字段名：id, name, data
-- 索引名：ix_1
```

---

## 8. 常见问题

### Q1: 何时使用staging目录？

当需要快速验证想法或进行开发测试时使用staging目录。stable的代码应移至schemas/。

### Q2: 迁移文件可以修改吗？

不可以。一旦提交到版本控制的迁移文件不应修改。如需变更，创建新的迁移。

### Q3: 如何处理大型种子数据？

将大型种子数据放入`seeds/bulk/`目录，或使用外部CSV文件加载。

### Q4: 多个项目共享数据库怎么办？

每个项目在自己的仓库维护Schema，通过`migrations/`目录的`shared/`子目录共享基础结构。

---

## 9. 检查清单

在提交数据库变更前，检查以下项目：

- [ ] 迁移脚本包含up.sql和down.sql
- [ ] 文件命名符合规范
- [ ] 添加必要的README文档
- [ ] 索引已添加到indexes/目录
- [ ] 函数已添加到functions/目录
- [ ] 触发器已添加到triggers/目录
- [ ] 测试脚本添加到tests/目录
- [ ] 更新SCHEMA.md文档

---

## 10. 参考资料

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [Supabase 文档](https://supabase.com/docs)
- [SQL Style Guide](https://www.sqlstyle.guide/)
- [GitHub - Database Best Practices](https://docs.github.com/en/actions/automating-your-workflow-with-github-actions/about-continuous-integration)

---

**文档版本**: 1.0.0  
**最后更新**: 2026-01-20  
**维护者**: 知识图谱项目组
