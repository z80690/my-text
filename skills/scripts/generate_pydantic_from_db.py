#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库表结构转Pydantic模型生成器
Database Schema to Pydantic Model Generator

功能: 从PostgreSQL/Supabase数据库表结构自动生成Pydantic模型

使用方法:
    python generate_pydantic_from_db.py --url <supabase_url> --key <anon_key>
    python generate_pydantic_from_db.py --tables users,contents,comments
    python generate_pydantic_from_db.py --output src/api/models

版本: 1.0.0
日期: 2026-01-20
"""

import argparse
import os
import sys
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

# 配置
DEFAULT_OUTPUT_DIR = "src/api/models"
TEMPLATE_HEADER = '''# -*- coding: utf-8 -*-
"""
自动生成的Pydantic模型
Auto-generated Pydantic Models

根据数据库表结构自动生成
Generated from database schema

版本: {version}
生成时间: {generated_at}
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


'''

TEMPLATE_MODEL = '''
class {class_name}(BaseModel):
    """{table_comment}"""
{fields}
'''

TEMPLATE_FIELD = '''    {field_name}: {field_type} {field_default} {field_description}'''

TEMPLATE_CREATE_MODEL = '''
class {class_name}Create(BaseModel):
    """创建模型"""
{fields}
'''

TEMPLATE_UPDATE_MODEL = '''
class {class_name}Update(BaseModel):
    """更新模型"""
{fields}
'''

TEMPLATE_RESPONSE_MODEL = '''
class {class_name}Response(BaseModel):
    """响应模型"""
{fields}
'''


# ============================================
# 类型映射
# ============================================

POSTGRES_TO_PYTHON = {
    # 字符串
    "varchar": "str",
    "character varying": "str",
    "text": "str",
    "char": "str",
    "bpchar": "str",
    # 整数
    "integer": "int",
    "int": "int",
    "int4": "int",
    "int8": "int",
    "bigint": "int",
    "smallint": "int",
    # 浮点数
    "decimal": "float",
    "numeric": "float",
    "real": "float",
    "double precision": "float",
    # 布尔
    "boolean": "bool",
    "bool": "bool",
    # UUID
    "uuid": "UUID",
    # 时间
    "timestamp": "datetime",
    "timestamptz": "datetime",
    "date": "date",
    "time": "datetime",
    "timetz": "datetime",
    # JSON
    "json": "Dict[str, Any]",
    "jsonb": "Dict[str, Any]",
    # 数组
    "text[]": "List[str]",
    "integer[]": "List[int]",
    "uuid[]": "List[UUID]",
    # BYTEA
    "bytea": "bytes",
}

POSTGRES_TO_DEFAULT = {
    "varchar": '= ""',
    "text": '= ""',
    "integer": "= 0",
    "int": "= 0",
    "bigint": "= 0",
    "smallint": "= 0",
    "decimal": "= 0.0",
    "numeric": "= 0.0",
    "real": "= 0.0",
    "double precision": "= 0.0",
    "boolean": "= False",
    "bool": "= False",
    "uuid": "= None",
    "timestamp": "= None",
    "timestamptz": "= None",
    "date": "= None",
    "json": "= {}",
    "jsonb": "= {}",
}

NEED_OPTIONAL = [
    "varchar", "text", "integer", "bigint", "smallint",
    "decimal", "numeric", "real", "double precision",
    "boolean", "uuid", "timestamp", "timestamptz", "date",
    "json", "jsonb", "text[]", "integer[]", "uuid[]"
]


# ============================================
# 数据库连接
# ============================================

def get_table_info(connection, table_name: str) -> Tuple[List[Dict], str]:
    """获取表结构信息"""
    query = '''
        SELECT 
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default,
            c.character_maximum_length,
            pg_catalog.col_description(a.attrelid, a.attnum) as description
        FROM information_schema.columns c
        LEFT JOIN pg_catalog.pg_class t ON c.table_name = t.relname
        LEFT JOIN pg_catalog.pg_namespace n ON t.relnamespace = n.oid
        LEFT JOIN pg_catalog.pg_attribute a ON a.attrelid = t.oid AND c.column_name = a.attname
        WHERE c.table_name = %s
        ORDER BY c.ordinal_position
    '''
    
    cursor = connection.cursor()
    cursor.execute(query, (table_name,))
    columns = cursor.fetchall()
    cursor.close()
    
    # 获取表注释
    cursor = connection.cursor()
    cursor.execute(f'''
        SELECT COALESCE(obj_description(%s::regclass), '{table_name}')
    ''', (table_name,))
    table_comment = cursor.fetchone()[0]
    cursor.close()
    
    return columns, table_comment


def get_all_tables(connection) -> List[str]:
    """获取所有表名"""
    cursor = connection.cursor()
    cursor.execute('''
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    ''')
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables


# ============================================
# 代码生成
# ============================================

def map_column_type(pg_type: str) -> str:
    """映射PostgreSQL类型到Python类型"""
    # 处理数组类型
    if pg_type.endswith("[]"):
        base_type = pg_type[:-2]
        python_base = POSTGRES_TO_PYTHON.get(base_type, "Any")
        return f"List[{python_base}]"
    
    return POSTGRES_TO_PYTHON.get(pg_type, "Any")


def is_optional(pg_type: str, is_nullable: str) -> bool:
    """判断是否需要Optional"""
    return pg_type in NEED_OPTIONAL and is_nullable == "YES"


def format_field_name(column_name: str) -> str:
    """格式化字段名"""
    # 保留原始名称，转为snake_case
    return column_name.lower()


def generate_field(
    column_name: str,
    pg_type: str,
    is_nullable: str,
    default: Optional[str],
    description: Optional[str]
) -> str:
    """生成字段定义"""
    python_type = map_column_type(pg_type)
    field_name = format_field_name(column_name)
    
    # 判断是否需要Optional
    if is_nullable == "YES":
        if "List" in python_type:
            field_type = f"Optional[{python_type}]"
        elif python_type in ["str", "int", "float", "bool"]:
            field_type = f"Optional[{python_type}]"
        else:
            field_type = f"Optional[{python_type}]"
        field_default = "= None"
    else:
        field_type = python_type
        if default:
            field_default = f"= {default}"
        elif "List" in python_type:
            field_default = "= None"
        else:
            field_default = "= None"
    
    # 描述
    if description:
        field_desc = f'# {description}'
    else:
        field_desc = ""
    
    return TEMPLATE_FIELD.format(
        field_name=field_name,
        field_type=field_type,
        field_default=field_default,
        field_description=field_desc
    )


def generate_model(table_name: str, columns: List[Dict], table_comment: str) -> str:
    """生成模型代码"""
    class_name = to_pascal_case(table_name)
    
    # 生成字段
    fields = []
    for col in columns:
        field_code = generate_field(
            column_name=col[0],
            pg_type=col[1],
            is_nullable=col[2],
            default=col[3],
            description=col[4]
        )
        fields.append(field_code)
    
    return TEMPLATE_MODEL.format(
        class_name=class_name,
        table_comment=table_comment,
        fields="\n".join(fields)
    )


def to_pascal_case(table_name: str) -> str:
    """表名转PascalCase类名"""
    # 处理复数形式
    if table_name.endswith("s"):
        base_name = table_name[:-1]
    else:
        base_name = table_name
    
    # 转换为PascalCase
    words = base_name.replace("-", "_").replace(".", "_").split("_")
    return "".join(word.capitalize() for word in words if word)


def to_snake_case(name: str) -> str:
    """转换为snake_case"""
    return name.lower().replace("-", "_")


# ============================================
# 主程序
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description="从数据库表结构生成Pydantic模型"
    )
    parser.add_argument("--url", help="Supabase URL", default=os.environ.get("SUPABASE_URL"))
    parser.add_argument("--key", help="Supabase Anon Key", default=os.environ.get("SUPABASE_KEY"))
    parser.add_argument("--tables", help="指定表名，逗号分隔", default="")
    parser.add_argument("--output", help="输出目录", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--version", help="版本号", default="1.0.0")
    
    args = parser.parse_args()
    
    if not args.url or not args.key:
        print("错误: 请提供--url和--key参数，或设置环境变量SUPABASE_URL和SUPABASE_KEY")
        sys.exit(1)
    
    try:
        import psycopg2
    except ImportError:
        print("错误: 请安装psycopg2-binary: pip install psycopg2-binary")
        sys.exit(1)
    
    # 连接数据库
    try:
        # 从Supabase URL解析连接信息
        # 格式: https://xxx.supabase.co
        host = args.url.replace("https://", "").replace("http://", "").split(".")[0] + ".supabase.co"
        
        connection = psycopg2.connect(
            host="db." + host,
            port=5432,
            user="postgres",
            password=args.key,
            database="postgres"
        )
        print("✓ 数据库连接成功")
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        sys.exit(1)
    
    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    print(f"✓ 输出目录: {args.output}")
    
    # 获取表列表
    if args.tables:
        tables = args.tables.split(",")
        print(f"✓ 指定表: {tables}")
    else:
        tables = get_all_tables(connection)
        print(f"✓ 发现表: {len(tables)}个")
    
    # 生成模型
    generated_files = []
    for table in tables:
        print(f"\n处理表: {table}")
        
        try:
            columns, table_comment = get_table_info(connection, table)
            print(f"  - 字段数: {len(columns)}")
            
            model_code = generate_model(table, columns, table_comment)
            
            # 保存文件
            file_name = f"{to_snake_case(table)}.py"
            file_path = os.path.join(args.output, file_name)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(TEMPLATE_HEADER.format(
                    version=args.version,
                    generated_at=datetime.now().isoformat()
                ))
                f.write(model_code)
            
            print(f"  ✓ 生成: {file_name}")
            generated_files.append(file_name)
            
        except Exception as e:
            print(f"  ✗ 失败: {e}")
    
    # 生成__init__.py
    init_content = '''# -*- coding: utf-8 -*-
"""
自动生成的Pydantic模型
Auto-generated Pydantic Models
"""

'''
    
    for file_name in sorted(generated_files):
        module_name = file_name[:-3]  # 去掉.py
        class_name = to_pascal_case(module_name)
        init_content += f"from .{module_name} import {class_name}\n"
    
    init_content += f"\n__all__ = [\n"
    for file_name in sorted(generated_files):
        module_name = file_name[:-3]
        class_name = to_pascal_case(module_name)
        init_content += f'    "{class_name}",\n'
    init_content += "]\n"
    
    init_path = os.path.join(args.output, "__init__.py")
    with open(init_path, "w", encoding="utf-8") as f:
        f.write(init_content)
    
    print(f"\n✓ 生成__init__.py")
    print(f"\n{'='*50}")
    print(f"完成! 共生成 {len(generated_files)} 个模型文件")
    print(f"输出目录: {args.output}")
    print(f"{'='*50}")
    
    connection.close()


if __name__ == "__main__":
    main()
