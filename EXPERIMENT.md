# Skills Framework Experiment

**目标**：验证 skills 框架与 Supabase 数据库的集成

**预计时间**：30-60 分钟

---

## 实验结构

```
my-text/
├── skills/
│   ├── utils/__init__.py           # 工具函数（已补充）
│   ├── logic_chain/steps/database_node.py  # 数据库节点（新建）
│   ├── examples/db_query/          # 示例技能（新建）
│   │   ├── skill.json
│   │   ├── handler.py
│   │   └── README.md
│   └── skills.json                 # 技能注册表（已更新）
├── src/skill_handler.py            # 云函数入口（新建）
└── test_skill_db.py                # 测试脚本（新建）
```

---

## 前置条件

```bash
# 1. 安装依赖
pip install supabase

# 2. 设置环境变量（Windows）
set SUPABASE_URL=https://your-project.supabase.co
set SUPABASE_KEY=your-anon-key

# 或创建 .env 文件
echo SUPABASE_URL=https://your-project.supabase.co > .env
echo SUPABASE_KEY=your-anon-key >> .env
```

---

## 验证步骤

### Step 1: 检查环境变量

```bash
python -c "import os; print('SUPABASE_URL:', os.environ.get('SUPABASE_URL')); print('SUPABASE_KEY:', '***' if os.environ.get('SUPABASE_KEY') else 'NOT SET')"
```

**成功标志**：
- 输出包含有效的 URL 和 KEY

**失败标志**：
- `NOT SET` 或空值

---

### Step 2: 运行技能测试

```bash
python test_skill_db.py
```

**测试内容**：
1. **直接技能执行** - 调用 `db_query` 技能
2. **逻辑链执行** - 使用 `DatabaseNode` 查询数据
3. **条件分支** - IF/ELSE 逻辑演示

**成功标志**：
```
SUMMARY
Passed:   3
Failed:   0
Skipped:  0

[SUCCESS] All tests passed!
```

**失败标志**：
- `[FAIL]` 错误信息
- Supabase 连接失败（需要检查环境变量）

---

### Step 3: 测试云函数（可选）

```bash
python -c "
from src.skill_handler import main_handler
import json

event = {
    'httpMethod': 'GET',
    'path': '/health'
}
response = main_handler(event, None)
print(response)
"
```

**成功标志**：
```json
{
  "statusCode": 200,
  "body": "{\"status\": \"healthy\", \"service\": \"skills-framework\"}"
}
```

---

### Step 4: 验证数据库查询

如果 Supabase 中有 `users` 表，运行：

```python
from skills.examples.db_query.handler import handle

result = handle({
    "table": "users",
    "columns": "id,email",
    "limit": 5
})

print(result)
```

**成功标志**：
```json
{
  "success": true,
  "data": {
    "table": "users",
    "row_count": 5,
    "records": [...]
  }
}
```

---

## 预期结果

| 步骤 | 验证点 | 成功标志 |
|------|--------|----------|
| Step 1 | 环境变量 | URL 和 KEY 已设置 |
| Step 2 | 测试脚本 | 3 个测试全部通过 |
| Step 3 | 云函数 | 返回 200 + healthy |
| Step 4 | 数据库 | 返回记录数据 |

---

## 常见问题

### Q: `SUPABASE_URL not set`
**解决**：在 Windows 中运行：
```cmd
setx SUPABASE_URL "https://your-project.supabase.co"
```

### Q: `Module not found: supabase`
**解决**：安装依赖
```bash
pip install supabase
```

### Q: `Table 'users' not found`
**解决**：检查 Supabase 中的表名，或修改查询中的表名

---

## 后续扩展

实验成功后，可以：

1. **创建新技能**：使用模板 `cp -r skills/templates/basic skills/examples/my_skill`
2. **编排复杂逻辑**：在 `logic_chain` 中组合多个节点
3. **部署到云函数**：将 `src/skill_handler.py` 部署到腾讯云 SCF
