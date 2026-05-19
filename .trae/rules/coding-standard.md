# 编码规范 (L3)

**触发条件**：当对话涉及编写、修改、审查代码时自动加载。

## 命名规范
- 变量：`camelCase`（如 `userName`, `isActive`）
- 类：`PascalCase`（如 `UserService`, `ConfigLoader`）
- 常量：`UPPER_SNAKE_CASE`（如 `MAX_RETRY`, `API_KEY`）

## 代码风格
- 缩进：4空格
- 必须使用类型提示
- 导入顺序：标准库 → 第三方库 → 本地模块

## 禁止清单
- 硬编码配置值
- `var` 声明
- `console.log`
- 空占位符（`pass`）
- 一次性代码（无复用性）
