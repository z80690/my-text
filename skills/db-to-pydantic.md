# -*- coding: utf-8 -*-
"""
技能：根据数据库表结构自动生成Pydantic模型
Skill: Auto-generate Pydantic Models from Database Schema

此技能用于从PostgreSQL/Supabase数据库表结构自动生成Pydantic模型代码。

## 使用方法

```bash
# 方式1: 在OpenSpec中调用
/skill db-to-pydantic

# 方式2: 直接运行脚本
python scripts/generate_pydantic_from_db.py --url <supabase_url> --key <anon_key>

# 方式3: 指定表生成
python scripts/generate_pydantic_from_db.py --tables users,contents,comments
```

## 功能特性

- 自动连接Supabase/PostgreSQL数据库
- 读取表结构（列名、类型、约束）
- 生成对应的Pydantic模型代码
- 支持外键关系生成关联模型
- 生成CRUD操作的Pydantic模型
- 支持批量生成所有表或指定表

## 前置要求

- 安装依赖: pip install psycopg2-binary supabase
- 配置环境变量: SUPABASE_URL, SUPABASE_KEY

## 输出

- 生成 `src/api/models/` 目录
- 每个表生成一个模型文件
- 生成主导入文件 `src/api/models/__init__.py`

## 示例

输入数据库表:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

输出Pydantic模型:
```python
class User(BaseModel):
    id: Optional[UUID] = None
    username: Optional[str] = None
    email: str
    created_at: Optional[datetime] = None
```

---

**技能名称**: db-to-pydantic  
**技能类型**: 数据转换  
**适用场景**: 数据库迁移、API开发、代码生成
"""
