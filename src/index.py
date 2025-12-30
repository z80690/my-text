# -*- coding: utf8 -*-
import os
import json
from supabase import create_client, Client
from typing import Dict, Any

def main_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    SCF入口函数，连接Supabase并查询数据。
    """
    result = {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': ''
    }
    
    try:
        # 1. 从环境变量读取配置
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        # 验证环境变量
        if not supabase_url or not supabase_key:
            error_msg = "Error: SUPABASE_URL or SUPABASE_KEY is not set in environment variables"
            print(error_msg)
            result['statusCode'] = 400
            result['body'] = json.dumps({'error': error_msg})
            return result
        
        # 2. 创建Supabase客户端
        supabase: Client = create_client(supabase_url, supabase_key)
        print("Supabase client initialized successfully.")
        
        # 3. 执行查询（示例：从knowledge_base表查询前5条数据）
        # 请确保您的Supabase项目中存在此表
        response = supabase.table("knowledge_base").select("*").limit(5).execute()
        
        # 4. 处理查询结果
        print(f"Query executed successfully. Found {len(response.data)} records.")
        
        result['body'] = json.dumps({
            'success': True,
            'message': 'Query successful',
            'data': response.data,
            'count': len(response.data)
        }, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        result['statusCode'] = 500
        result['body'] = json.dumps({'error': error_msg})
    
    print("Supabase handler execution complete")
    return result