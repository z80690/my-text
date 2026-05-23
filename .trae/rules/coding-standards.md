# 编码标准

**版本**：v1.0
**更新日期**：2026-05-23
**规则状态**：✅ 生效中
**整合来源**：coding-standard.md + git-workflow.md
**触发条件**：编写/修改/审查代码时自动加载
**L1支撑**：环境感知、交付标准
**L2支撑**：质量规范

---

## 第一部分：编码规范

### 1.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量 | camelCase | `userName`, `totalCount` |
| 函数/方法 | camelCase | `calculateTotal()`, `getUser()` |
| 类 | PascalCase | `UserService`, `DataRepository` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| 私有成员 | 下划线前缀 | `_internalMethod()`, `_privateVar` |

### 1.2 代码风格

#### 缩进与空格
- **4 空格缩进**（不要用 Tab）
- 运算符两侧加空格：`a = b + c`
- 逗号后加空格：`func(a, b, c)`

#### 类型提示（必须使用）
```python
# ✅ 正确：完整的类型提示
def process_data(data: list[dict[str, int]]) -> dict[str, float]:
    """处理数据并返回结果"""

# ❌ 错误：没有类型提示
def process_data(data):
    ...
```

### 1.3 禁止事项

| 禁止 | 原因 | 替代方案 |
|------|------|----------|
| 硬编码密钥/Token | 安全风险 | 使用环境变量 |
| 使用 `var` (JS) | 过时语法 | 使用 `let`/`const` |
| 遗留 `console.log` | 调试代码 | 使用专业日志库 |
| 空占位符 (`pass`) | 未完成实现 | 提供完整实现 |

### 1.4 代码质量检查清单

交付前确认：
- [ ] 命名符合规范
- [ ] 有完整的类型提示
- [ ] 代码格式化完成 (black, prettier)
- [ ] 静态检查通过 (flake8, eslint)
- [ ] 无禁止事项
- [ ] 无测试调试代码残留

---

## 第二部分：Git工作流

### 2.1 分支策略

| 分支类型 | 命名规范 | 用途 | 保护 |
|----------|----------|------|------|
| main | main | 生产环境 | ✅ 保护 |
| 功能分支 | feat/xxx | 新功能开发 | - |
| 修复分支 | fix/xxx | Bug 修复 | - |
| 文档分支 | docs/xxx | 文档更新 | - |

### 2.2 提交信息规范

#### 格式
```
<type>(<scope>): <subject>

<body>  (可选)
<footer> (可选)
```

#### Type 类型

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档更新 |
| style | 代码格式调整 |
| refactor | 重构 |
| test | 测试相关 |
| chore | 构建/工具 |

#### 示例
```git
feat(auth): add JWT token validation

- add token verification middleware
- add unit tests for auth service
- update API documentation

Closes #123
```

### 2.3 提交前检查清单

- [ ] 测试通过
- [ ] 静态检查通过 (lint)
- [ ] 代码格式化完成
- [ ] 无遗留调试代码
- [ ] 提交信息符合规范

---

## 第三部分：代码审查流程

### 3.1 审查要点

#### 代码正确性
- [ ] 代码逻辑是否正确
- [ ] 是否有边界条件处理
- [ ] 是否有错误处理

#### 代码质量
- [ ] 是否符合命名规范
- [ ] 是否有适当的注释
- [ ] 是否有重复代码

#### 代码安全
- [ ] 是否有硬编码敏感信息
- [ ] 是否有SQL注入风险
- [ ] 是否有XSS风险

#### 代码性能
- [ ] 是否有明显的性能问题
- [ ] 是否有内存泄漏风险
- [ ] 是否有不必要的循环

### 3.2 审查意见分级

| 级别 | 说明 | 必须修改 |
|------|------|----------|
| Must Fix | 必须修改 | ✅ |
| Should Fix | 强烈建议修改 | ⚠️ |
| Consider | 建议考虑 | ☐ |
| Nitpick | 小问题 | ☐ |

### 3.3 审查反馈模板

```
## 代码审查反馈

### 必须修改
- [ ] [文件:行号] 问题描述
- [ ] [文件:行号] 问题描述

### 建议修改
- [ ] [文件:行号] 问题描述

### 总体评价
[评价内容]
```

---

## 第四部分：版本历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0 | 2026-05-23 | 整合coding-standard.md、git-workflow.md为单一编码标准文件 | 系统 |
