# 更新日志

## [2026-01-30] 依赖管理重大改进

### 🐛 修复的问题

#### 1. PyJWT 版本冲突（严重）
**问题**：`supabase-auth` 要求 `pyjwt>=2.10.1`，而 `zhipuai` 要求 `pyjwt>=2.8.0,<2.9.0`，导致无法同时满足两者要求。

**影响**：智谱AI 集成功能可能无法正常工作，依赖安装时会出现冲突警告。

**解决方案**：采用方案 A - 移除 `zhipuai` 依赖
- ✅ 项目代码中未实际使用 `zhipuai` 包
- ✅ 完全解决 PyJWT 版本冲突
- ✅ 保持 Supabase 生态系统的稳定性

**说明**：如果将来需要使用智谱AI，可以单独创建集成项目或寻找兼容的 SDK。

#### 2. zhipuai 版本不正确
**问题**：`requirements.txt` 中指定 `zhipuai==4.0.0`，但 PyPI 上不存在该版本。

**影响**：依赖安装时会失败。

**解决方案**：已移除该依赖（见问题 1 的解决方案）。

### ✨ 新增功能

#### 1. 版本管理改进
**变更**：将所有固定版本（`==`）改为兼容范围版本（`~=`）
- `supabase==2.27.0` → `supabase~=2.27.0`
- `httpx==0.28.1` → `httpx~=0.28.0`
- `pyjwt==2.8.0` → `pyjwt>=2.10.0`
- 其他所有包都改为兼容范围版本

**优势**：
- ✅ 自动获得 bug 修复和补丁更新
- ✅ 避免破坏性 API 更改
- ✅ 改善安全补丁的及时应用
- ✅ 减少维护负担

#### 2. 开发依赖分离
**变更**：创建 `src/requirements-dev.txt`
- 分离生产依赖和开发依赖
- 包含代码质量工具（pylint, black, isort, mypy）
- 包含安全审计工具（pip-audit）
- 包含依赖树工具（pipdeptree）

**优势**：
- ✅ 生产环境更轻量
- ✅ 开发环境工具齐全
- ✅ 明确依赖用途

#### 3. CI/CD 流程
**变更**：创建 `.github/workflows/ci-cd-pipeline.yml`

**包含的工作流**：
1. **安全扫描（security-scan）**
   - 运行 `pip-audit` 检查安全漏洞
   - 检测依赖冲突
   - 生成安全报告

2. **依赖安装（install）**
   - 使用 pip 缓存加速构建
   - 验证无依赖冲突
   - 安装生产依赖

3. **测试（test）**
   - 连通性测试
   - 认证系统测试
   - 数据库模式测试
   - 生成测试报告

4. **代码质量（code-quality）**
   - Pylint 代码检查
   - MyPy 类型检查
   - Black 格式检查
   - isort 导入排序检查

5. **OpenSpec 验证（openspec-validate）**
   - 验证所有 OpenSpec 规范
   - 严格模式检查

6. **Docker 构建（build）**
   - 构建 Docker 镜像
   - 测试 Docker 镜像
   - 可选推送到镜像仓库

7. **部署（deploy）**
   - 部署到腾讯云 SCF
   - 仅在 main 分支触发

**触发条件**：
- Push 到 main/develop 分支
- Pull Request
- 每日定时执行安全扫描（UTC 2:00）
- 手动触发（可跳过测试）

#### 4. 依赖管理文档
**变更**：创建 `DEPENDENCIES.md`
- 详细的依赖管理指南
- 版本策略说明
- 安全审计流程
- 故障排除指南

#### 5. Docker 优化
**变更**：创建 `.dockerignore`
- 排除不必要的文件
- 减小 Docker 镜像大小
- 加快构建速度

### 📊 影响分析

#### 依赖变化
| 操作 | 数量 | 详情 |
|------|------|------|
| 移除的依赖 | 1 | zhipuai (版本冲突，未使用) |
| 修改的依赖 | 13 | 从固定版本改为兼容范围版本 |
| 新增的开发依赖 | 8 | pipdeptree, pylint, pip-audit, black, isort, mypy, pytest, sphinx |

#### 安全性改进
- ✅ 自动安全扫描（每日）
- ✅ 依赖冲突检测
- ✅ 漏洞及时更新（兼容范围版本）
- ✅ 代码质量检查（类型检查、格式化）

#### 开发体验改进
- ✅ 明确的依赖分离
- ✅ 完整的代码质量工具链
- ✅ 自动化 CI/CD 流程
- ✅ 详细的文档

### 🔄 迁移指南

#### 对于开发者
如果您已经有虚拟环境：

```bash
# 1. 激活虚拟环境
my_clean_venv\Scripts\activate  # Windows
# 或
source my_clean_venv/bin/activate  # Unix/macOS

# 2. 更新依赖
cd src
pip install --upgrade -r requirements.txt
pip install -r requirements-dev.txt

# 3. 验证无冲突
pipdeptree | grep -i "possibly conflicting" || echo "✅ 无冲突"
```

#### 对于部署环境
Docker 镜像会自动使用新的 requirements.txt，无需手动干预。

### 📝 后续建议

#### 短期（1-2 周）
1. 监控 CI/CD 流程，确保所有作业正常执行
2. 测试代码质量工具（pylint, mypy, black）配置
3. 验证 pip-audit 扫描结果

#### 中期（1-2 月）
1. 评估是否需要智谱 AI 功能，如需要，研究兼容的解决方案
2. 考虑添加更多测试用例提高覆盖率
3. 优化 Docker 镜像大小和构建时间

#### 长期（3-6 月）
1. 考虑使用 `poetry` 或 `pipenv` 替代 `requirements.txt`
2. 集成更多安全工具（如 bandit）
3. 添加性能测试和基准测试

### 🎯 总结

本次更新显著改善了项目的依赖管理和安全实践：

✅ **解决了 PyJWT 版本冲突**，确保依赖兼容性
✅ **改进了版本策略**，使用兼容范围版本
✅ **分离了开发依赖**，生产环境更轻量
✅ **建立了完整的 CI/CD 流程**，包括安全扫描和代码质量检查
✅ **提供了详细的文档**，便于开发者理解和使用

这些改进将提高项目的可维护性、安全性和开发效率。
