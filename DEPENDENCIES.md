# 依赖管理指南

本文档说明 my-text 项目的依赖管理最佳实践。

## 依赖文件说明

### requirements.txt
生产环境依赖，包含应用程序运行所需的所有核心包：
- Supabase 生态系统（supabase, realtime, storage3, supabase-auth, supabase-functions, postgrest）
- HTTP 客户端（httpx, httpcore, h11, yarl）
- 认证和安全（pyjwt, cryptography）
- 配置管理（python-dotenv）

**版本策略**：使用 `~=` 兼容范围版本
- `~=` 表示兼容的发布版本（兼容 API 更改）
- 例如：`~=`2.27.0` 接受 >=2.27.0 且 <2.28.0 的版本
- 优势：自动获得 bug 修复和补丁更新，避免破坏性更改

### requirements-dev.txt
开发环境依赖，仅用于开发、测试和代码质量检查：
- `pipdeptree` - 依赖树可视化
- `pylint` - Python 代码质量检查
- `pip-audit` - 安全漏洞扫描
- `black` - 代码格式化
- `isort` - 导入排序
- `mypy` - 类型检查
- `pytest` - 测试框架
- `sphinx` - 文档生成

**注意**：这些依赖不应安装到生产环境。

## 安装依赖

### 生产环境
```bash
cd src
pip install -r requirements.txt
```

### 开发环境
```bash
cd src
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 使用虚拟环境（推荐）
```bash
# 创建虚拟环境（如果不存在）
python -m venv my_clean_venv

# Windows 激活
my_clean_venv\Scripts\activate

# Unix/macOS 激活
source my_clean_venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 依赖版本管理

### 查看已安装的包
```bash
pip list
```

### 查看依赖树
```bash
pipdeptree
```

### 检查依赖冲突
```bash
pipdeptree | grep -i "possibly conflicting"
```

### 检查过期的包
```bash
pip list --outdated
```

### 更新依赖

**更新单个包到兼容范围内最新版本**：
```bash
pip install --upgrade package-name
```

**更新所有生产依赖**：
```bash
pip install --upgrade -r requirements.txt
```

**更新所有开发依赖**：
```bash
pip install --upgrade -r requirements-dev.txt
```

## 安全审计

### 运行 pip-audit
```bash
pip-audit --desc
```

### 生成详细的安全报告
```bash
pip-audit --desc --format json > security-report.json
```

### 配置 pip-audit 忽略特定漏洞（谨慎使用）
```bash
pip-audit --desc --ignore vuln-id-1,vuln-id-2
```

## CI/CD 流程

项目配置了完整的 CI/CD 流程，包括：

### 1. 安全扫描（security-scan job）
- 依赖审计（pip-audit）
- 安全漏洞检查
- 依赖冲突检测
- 生成安全报告

### 2. 依赖安装（install job）
- 使用 pip 缓存加速构建
- 验证无依赖冲突
- 安装生产依赖

### 3. 测试（test job）
- 连通性测试
- 认证系统测试
- 数据库模式测试
- 生成测试报告

### 4. 代码质量（code-quality job）
- Pylint 代码检查
- MyPy 类型检查
- Black 格式检查
- isort 导入排序检查

### 5. OpenSpec 验证（openspec-validate job）
- 验证所有 OpenSpec 规范
- 严格模式检查

### 6. Docker 构建（build job）
- 构建 Docker 镜像
- 测试 Docker 镜像
- 可选：推送到镜像仓库

### 7. 部署（deploy job）
- 部署到腾讯云 SCF
- 仅在 main 分支触发

## 最佳实践

### 1. 版本控制
- ✅ 使用 `~=` 兼容范围版本
- ❌ 避免固定版本（`==`），除非有特殊原因
- ❌ 避免完全开放的版本（如 `*` 或无版本说明符）

### 2. 依赖分离
- ✅ 生产依赖放在 `requirements.txt`
- ✅ 开发依赖放在 `requirements-dev.txt`
- ✅ 测试依赖放在 `requirements-dev.txt`

### 3. 定期维护
- ✅ 每月检查安全漏洞（`pip list --outdated`）
- ✅ 定期运行 `pip-audit`
- ✅ 及时更新依赖到安全版本

### 4. 文档更新
- ✅ 更新此文档当添加新依赖时
- ✅ 记录添加新依赖的原因
- ✅ 标记可选依赖

### 5. 虚拟环境
- ✅ 始终使用虚拟环境
- ✅ 不要提交虚拟环境到 git
- ✅ 在 .dockerignore 中排除虚拟环境

## 故障排除

### 依赖冲突
如果遇到依赖冲突：
```bash
# 查看冲突详情
pipdeptree | grep -i "possibly conflicting"

# 解决方案：
# 1. 更新冲突的包到兼容版本
# 2. 使用 pipdeptree 查看完整的依赖链
# 3. 考虑移除不必要的依赖
```

### 安全漏洞
如果发现安全漏洞：
```bash
# 查看漏洞详情
pip-audit --desc

# 解决方案：
# 1. 更新到修复版本
# 2. 临时忽略（仅当评估后确认无风险）
pip-audit --desc --ignore VULN-ID
```

### 安装失败
如果依赖安装失败：
```bash
# 清理缓存
pip cache purge

# 重新安装
pip install --upgrade -r requirements.txt
```

## 相关文件

- `src/requirements.txt` - 生产环境依赖
- `src/requirements-dev.txt` - 开发环境依赖
- `.github/workflows/ci-cd-pipeline.yml` - CI/CD 配置
- `.dockerignore` - Docker 构建排除文件
- `CODEBUDDY.md` - 项目架构和开发指南

## 支持

如有问题，请参考：
- [pip 文档](https://pip.pypa.io/)
- [pip-audit 文档](https://pip-audit.readthedocs.io/)
- [PyPI](https://pypi.org/)
