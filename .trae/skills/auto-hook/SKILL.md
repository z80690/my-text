# Auto-Hook Skill

## 功能
自动化钩子：在关键事件自动触发指定操作

## 使用场景

| 触发时机 | 自动执行 | 使用场景 |
|---------|---------|---------|
| `pre-commit` | lint + 格式化检查 | 提交前代码质量把控 |
| `post-generate` | 运行相关测试 | 生成代码后立即验证 |
| `file-save` | 触发增量构建 | 保存文件后快速预览 |
| `pre-build` | 依赖检查 | 构建前确保环境正确 |
| `post-deploy` | 健康检查 | 部署后验证服务状态 |

## 使用方式
```
你: 设置一个hook，在提交前运行lint
你: 添加一个post-generate hook，生成代码后自动测试
```

## 实现方式

### Hook配置结构
```json
{
  "trigger": "pre-commit|post-generate|file-save|pre-build|post-deploy",
  "action": "lint|test|build|format|health-check",
  "config": {
    "timeout": 30,
    "fail_on_error": true
  }
}
```

## 执行流程

### 1. 触发检测
- 监听事件类型
- 判断是否匹配配置的hook

### 2. 执行动作
- 运行指定命令
- 捕获输出和结果

### 3. 结果处理
- 成功：记录日志，继续流程
- 失败：根据配置决定是否阻止

## 输出格式
```
【Hook触发】
事件: pre-commit
执行: eslint + prettier
结果: ✅ 通过 (12.3s)
```
