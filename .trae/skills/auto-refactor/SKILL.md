# Auto-Refactor Skill v2.0

## 功能
全局代码重构：批量安全重构整个项目，保持功能不变

## 使用方式
```
你: 重构所有Class组件为Hooks
你: 统一所有接口地址
你: 批量修改变量命名风格
你: 提取这段代码为方法
你: 将重复代码抽取为函数
```

## 重构场景（增强版）

| 场景 | 说明 | 示例 | 快捷键 |
|------|------|------|--------|
| **语法迁移** | 旧语法转新语法 | Class→Hooks, callback→async/await | - |
| **命名统一** | 统一命名风格 | snake_case→camelCase | - |
| **模式替换** | 设计模式优化 | 观察者→事件总线 | - |
| **结构重组** | 目录结构优化 | 扁平→分层 | - |
| **冗余清理** | 删除重复代码 | 提取公共函数 | - |
| **Extract Method** | 代码块提取为方法 | 选中代码→提取为独立方法 | Ctrl+Alt+M |
| **Extract Constant** | 魔法数字提取为常量 | 42→MAX_RETRY | Ctrl+Alt+C |
| **Extract Variable** | 复杂表达式提取 | 计算式→变量 | Ctrl+Alt+V |
| **Extract Parameter** | 参数提取 | 硬编码→参数 | Ctrl+Alt+P |
| **Rename** | 智能重命名 | 自动更新所有引用 | Shift+F6 |
| **Change Signature** | 修改方法签名 | 添加/删除参数 | Ctrl+F6 |
| **Inline** | 内联展开 | 方法调用→直接代码 | Ctrl+Alt+N |
| **Safe Delete** | 安全删除 | 检查引用后删除 | Alt+Delete |
| **Extract Component** | React组件提取 | JSX片段→独立组件 | - |

## 执行流程（增强版）

### 1. 智能分析
- 全局搜索目标代码
- 分析影响范围（跨文件引用）
- 检测潜在冲突
- 制定修改计划

### 2. 预览确认
- 显示变更预览
- 列出受影响文件
- 支持选择性应用
- 冲突标记与处理建议

### 3. 安全重构
- 创建备份点（自动快照）
- 逐文件修改
- 保持引用一致
- 实时错误检测

### 4. 验证保证
- 运行测试确保功能不变
- 检查语法错误
- 验证边界情况
- 生成重构报告

## 框架特定重构

### React 重构
| 操作 | 说明 |
|------|------|
| Extract Component | 从现有组件提取JSX为独立组件 |
| Convert to Class | 函数组件→类组件 |
| Convert to Functional | 类组件→函数组件（自动转换Hooks） |
| Rename Component | 组件重命名（更新import） |

### Vue 重构
| 操作 | 说明 |
|------|------|
| Extract Component | 提取模板片段为子组件 |
| Extract Computed | 复杂表达式→computed属性 |

## 安全保障

| 机制 | 说明 |
|------|------|
| 引用追踪 | 跨文件引用分析 |
| 备份机制 | 重构前自动创建快照 |
| 回滚支持 | 一键撤销重构 |
| 冲突检测 | 检测潜在问题并提示 |
| 测试验证 | 自动运行相关测试 |

## 输出格式
```
【重构计划】
范围: 23个文件
修改: 156处
预计风险: 低

【变更预览】
✓ src/utils/helpers.js: 提取方法 getStatusText()
✓ src/components/Header.jsx: 重命名 headerTitle → pageTitle
✓ src/api/client.js: 修改函数签名 addParam()

【执行结果】
成功: ✅ 23/23
测试: ✅ 通过
备份: ✅ 已创建 (backup_20240115_1030.zip)
```

## 配置选项

```yaml
# .auto-refactor.yaml
rules:
  naming_convention: camelCase  # camelCase, snake_case, PascalCase
  max_method_length: 50
  max_nesting_level: 4
  remove_unused_imports: true
  sort_imports: true
  
preview:
  enabled: true
  show_diffs: true
  
safety:
  create_backup: true
  run_tests: true
  dry_run_only: false
```

## 支持语言
- JavaScript/TypeScript
- Python
- Java
- Go
- Rust
- Vue/React（框架特定）