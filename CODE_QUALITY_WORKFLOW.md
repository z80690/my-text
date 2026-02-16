# 代码质量守护工作流 - 使用指南

## 快速开始

```bash
# 进入后端目录
cd backend

# 全量检查（OpenSpec + ESLint + Prettier）
npm run quality:check

# 修复所有问题
npm run quality:fix
```

## 可用命令

### ESLint（代码质量检查）
```bash
npm run lint          # 检查代码问题
npm run lint:fix      # 自动修复可修复的问题
npm run lint:watch    # 持续监控文件变化
```

### Prettier（代码格式化）
```bash
npm run format          # 格式化所有文件
npm run format:check    # 检查是否需要格式化
npm run format:diff     # 显示格式差异
npm run format:watch    # 持续监控并格式化
```

### OpenSpec（接口规范检查）
```bash
npm run spec:check          # 验证所有规范
npm run spec:check:strict   # 严格模式验证
```

### 守护进程（开发模式）
```bash
npm run dev:lint    # ESLint 守护进程
npm run dev:format  # Prettier 守护进程
npm run dev:all     # 启动所有守护进程
```

## 触发方式

通过 oh-my-opencode 自然语言触发：

| 指令 | 执行内容 |
|------|----------|
| "全量检查" | OpenSpec + ESLint + Prettier + pylint |
| "检查接口规范" | 仅 OpenSpec |
| "修复代码风格" | 仅 Prettier |
| "语法检查" | ESLint + pylint（JS/TS + Python） |
| "代码检查" | ESLint + Prettier + pylint |

## Python 代码检查（pylint）

### 基本用法

```bash
cd src
python -m pylint . --output-format=styled
```

### 检测类型错误

对于类型错误检测（如 `encoding='r'`），需要在代码中添加类型注解：

```python
def open_file(path: str, encoding: str) -> None:
    with open(path, encoding=encoding) as f:
        return f.read()

# 正确用法
open_file("test.txt", encoding="utf-8")

# 错误用法 - 会触发类型检查警告
def process(encoding: int) -> None:
    pass

process(encoding="r")  # Type checker 会报错
```

### 推荐的类型检查工具

对于严格的类型检查，建议额外安装 mypy：

```bash
pip install mypy
mypy your_code.py
```

## 配置文件

| 文件 | 说明 |
|------|------|
| `backend/eslint.config.js` | ESLint 配置（Flat Config 格式） |
| `backend/prettier.config.js` | Prettier 配置 |
| `backend/.prettierignore` | Prettier 忽略列表 |
| `src/.pylintrc` | Pylint 配置（Python 代码检查） |
| `openspec/workflows/code-quality.yml` | oh-my-opencode 工作流 |

## 文件结构

```
my-text/
├── backend/
│   ├── package.json              # 已配置所有 scripts
│   ├── eslint.config.js          # ESLint 配置
│   ├── prettier.config.js        # Prettier 配置
│   ├── .prettierignore           # 忽略列表
│   └── .opencode/
│       └── workflows/
│           └── README.md         # 工作流说明
├── openspec/
│   ├── workflows/
│   │   └── code-quality.yml      # 工作流配置
│   ├── specs/
│   │   ├── user-auth/
│   │   ├── authentication/
│   │   └── user-profile/
│   └── project.md
└── ...
```

## 工作流架构

```
用户指令 (oh-my-opencode)
        ↓
   指挥中枢 (并行调度)
        ↓
   ┌─────┴─────┬──────────┐
   ↓           ↓          ↓
OpenSpec    ESLint    Prettier
(规范检查)  (语法检查) (代码格式化)
   ↓           ↓          ↓
   └─────────┬─┴──────────┘
             ↓
        结果汇总
```

## 验证测试

```bash
# 1. ESLint 测试
cd backend && npx eslint . --format stylish

# 2. Prettier 测试
npx prettier --check . --ignore-path .prettierignore

# 3. OpenSpec 测试
cd .. && npx openspec validate --all --json

# 4. 完整测试
cd backend && npm run quality:check
```

## VS Code 集成（推荐）

创建 `.vscode/settings.json`：

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "eslint.enable": true,
  "eslint.validate": ["javascript", "python"],
  "eslint.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  }
}
```

## 常见问题

### Q: 如何添加新的检查规则？

编辑 `backend/eslint.config.js`：

```javascript
{
  rules: {
    "new-rule": "error",  // 或 "warn"
  }
}
```

### Q: 如何忽略特定文件？

编辑 `backend/.prettierignore` 和 `backend/eslint.config.js` 的 ignores 数组。

对于 Python 文件，在 `src/.pylintrc` 中添加：

```
ignore=test_*.py
```

### Q: 如何更新 Prettier 配置？

编辑 `backend/prettier.config.js`，然后运行：

```bash
cd backend && npm run format
```

### Q: pylint 能检测所有类型错误吗？

pylint 主要关注代码质量，对于严格的类型检查（如 `encoding='r'`），建议：

1. **添加类型注解**：
```python
def process(encoding: int) -> None:
    pass
```

2. **使用 mypy 进行严格类型检查**：
```bash
pip install mypy
mypy your_code.py
```

3. **IDE 集成**：使用 VS Code + Pyright 获得实时类型检查
