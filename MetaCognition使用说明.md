# Meta-Cognition 使用说明 - 完全无感模式

## 🚀 完全无感！导入即用！

### 最简单的使用方式

```python
# 只需要这一行！自动启动！完全无感！
from meta_cognition_manager import auto_submit, auto_complete

# 直接用！不需要任何启动操作！
session_id = auto_submit("请帮我优化代码")
auto_complete(session_id, "success")
```

---

## 📁 文件结构

```
my-text/
├── meta-cognition-manager.py    ← 核心管理器（自动启动）
├── test_seamless.py             ← 无感模式测试
├── meta-cognition-data/         ← 数据存储（独立于 .trae）
│   └── logs/meta_cognition.json
└── .trae/                       ← 完全不碰！避免权限问题
```

---

## 🎯 使用示例

### 方式1: 完全无感（推荐）

```python
# 🔥 只需要导入！自动启动！
from meta_cognition_manager import auto_submit, auto_complete

# 直接提交任务
session_id = auto_submit("请帮我优化这段代码，提升性能")

# 完成任务
auto_complete(
    session_id,
    result="success",
    agents_used=["code_executor_agent"],
    duration_ms=1500
)
```

### 方式2: 使用装饰器（更无感！）

```python
from meta_cognition_manager import auto_track

# 🔥 自动跟踪函数执行！
@auto_track
def my_task():
    # 你的代码
    return "完成"

# 调用时自动记录！完全无感！
result = my_task()
```

### 方式3: 获取统计

```python
from meta_cognition_manager import auto_get_statistics

stats = auto_get_statistics()
print(f"总任务: {stats['total_tasks']}")
print(f"成功率: {stats['success_rate']}%")
```

---

## ✅ 完全无感特性

| 特性 | 说明 |
|------|------|
| **自动启动** | 导入模块时自动启动，无需手动操作 |
| **无需配置** | 开箱即用，无需任何配置 |
| **权限安全** | 数据存储在项目根目录，不碰 .trae |
| **完全静默** | 无任何启动提示（可选显示） |
| **自动记录** | 所有任务自动记录和统计 |

---

## 🔍 三种博弈模式自动识别

| 任务类型 | 触发关键词 |
|---------|-----------|
| **辩论模式** | 对比、权衡、优缺点、比较、分析 |
| **降维打击模式** | 优化、改进、提升、完善、修改、重构 |
| **深度设计模式** | 设计、架构、实现、创建、开发 |

---

## 📝 完整示例

创建 `my_app.py`：

```python
from meta_cognition_manager import auto_submit, auto_complete, auto_get_statistics

# 业务代码
def process_task(task_description):
    # 自动提交任务（完全无感！）
    session_id = auto_submit(task_description)
    
    # 执行任务...
    result = "success"
    
    # 自动完成任务
    auto_complete(
        session_id,
        result=result,
        agents_used=["code_executor_agent"],
        duration_ms=1000
    )
    return result

# 使用
process_task("请帮我优化代码")
process_task("对比两个技术方案")
process_task("设计一个系统")

# 查看统计
stats = auto_get_statistics()
print(f"完成任务数: {stats['total_tasks']}")
```

---

## 🔥 总结

```python
# 这就是全部！完全无感！
from meta_cognition_manager import auto_submit, auto_complete

session_id = auto_submit("你的任务")
auto_complete(session_id, "success")
```

✅ **不需要启动**  
✅ **不需要配置**  
✅ **导入即可用**  
✅ **完全无感体验**
