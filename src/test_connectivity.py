# -*- coding: utf-8 -*-
# 云函数连通性集成测试脚本
import os
import sys
import json
from typing import Dict, Any, Optional
from supabase import create_client, Client

def test_env_vars(supabase_url: Optional[str] = None, supabase_key: Optional[str] = None) -> Dict[str, Any]:
    """
    测试环境变量是否已正确设置
    允许通过参数传入URL和KEY，提高测试灵活性
    """
    url = supabase_url or os.getenv("SUPABASE_URL")
    key = supabase_key or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        return {"test": "environment_variables", "status": "FAILED", 
                "message": "SUPABASE_URL 或 SUPABASE_KEY 未设置"}
    return {"test": "environment_variables", "status": "PASSED", 
            "message": "环境变量检查通过"}

def test_supabase_connection(supabase_url: Optional[str] = None, 
                            supabase_key: Optional[str] = None) -> Dict[str, Any]:
    """测试Supabase客户端连接"""
    try:
        url = supabase_url or os.getenv("SUPABASE_URL")
        key = supabase_key or os.getenv("SUPABASE_KEY")
        if not url or not key:
            return {"test": "supabase_connection", "status": "FAILED", 
                    "message": "缺少连接参数"}
        
        supabase: Client = create_client(url, key)
        return {"test": "supabase_connection", "status": "PASSED", 
                "message": "Supabase客户端创建成功"}
    except Exception as e:
        return {"test": "supabase_connection", "status": "FAILED", 
                "message": f"连接失败: {str(e)}"}

def test_db_query(supabase_url: Optional[str] = None, 
                 supabase_key: Optional[str] = None) -> Dict[str, Any]:
    """测试数据库查询"""
    try:
        url = supabase_url or os.getenv("SUPABASE_URL")
        key = supabase_key or os.getenv("SUPABASE_KEY")
        if not url or not key:
            return {"test": "database_query", "status": "FAILED", 
                    "message": "缺少连接参数"}
        
        supabase: Client = create_client(url, key)
        # 执行一个简单的查询（从 knowledge_base 表获取1条数据）
        response = supabase.table("knowledge_base").select("*").limit(1).execute()
        return {"test": "database_query", "status": "PASSED", 
                "message": f"查询成功，获取到 {len(response.data)} 条数据", 
                "data": response.data[:1]}  # 只返回第一条数据避免输出过大
    except Exception as e:
        return {"test": "database_query", "status": "FAILED", 
                "message": f"查询失败: {str(e)}"}

def run_connectivity_tests(supabase_url: Optional[str] = None, 
                          supabase_key: Optional[str] = None) -> Dict[str, Any]:
    """
    【新入口函数】执行所有连通性测试
    与 main_handler 区分，专门用于本地或直接调用测试
    
    参数:
        supabase_url: 可选的Supabase URL，若不提供则从环境变量读取
        supabase_key: 可选的Supabase Key，若不提供则从环境变量读取
    
    返回:
        包含所有测试结果的字典
    """
    print("[INFO] 开始执行连通性测试 (run_connectivity_tests)...")
    
    # 执行所有测试
    test_results = []
    test_results.append(test_env_vars(supabase_url, supabase_key))
    test_results.append(test_supabase_connection(supabase_url, supabase_key))
    test_results.append(test_db_query(supabase_url, supabase_key))
    
    # 检查是否有测试失败
    all_passed = all(result["status"] == "PASSED" for result in test_results)
    
    response_body = {
        "message": "连通性测试完成 (via run_connectivity_tests)",
        "all_tests_passed": all_passed,
        "results": test_results
    }
    
    print(f"[INFO] 测试完成。全部通过: {all_passed}")
    return response_body

def main_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    【原入口函数】主处理函数，执行所有连通性测试
    返回格式符合云函数HTTP响应要求
    保持原样以兼容云函数调用
    """
    print("[INFO] 开始执行连通性测试 (main_handler)...")
    
    # 执行所有测试
    test_results = []
    test_results.append(test_env_vars())
    test_results.append(test_supabase_connection())
    test_results.append(test_db_query())
    
    # 检查是否有测试失败
    all_passed = all(result["status"] == "PASSED" for result in test_results)
    
    response_body = {
        "message": "连通性测试完成",
        "all_tests_passed": all_passed,
        "results": test_results
    }
    
    response = {
        "statusCode": 200 if all_passed else 500,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response_body, ensure_ascii=False)
    }
    
    print(f"[INFO] 测试完成。全部通过: {all_passed}")
    return response

if __name__ == "__main__":
    """
    直接运行脚本时的入口
    1. 支持通过命令行参数传递URL和KEY
    2. 支持从环境变量读取
    3. 提供清晰的用户交互
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='运行Supabase连通性测试')
    parser.add_argument('--url', help='Supabase项目URL', default=None)
    parser.add_argument('--key', help='Supabase API密钥', default=None)
    args = parser.parse_args()
    
    print("=" * 50)
    print("Supabase连通性测试工具")
    print("=" * 50)
    
    # 确定使用的URL和KEY
    url = args.url
    key = args.key
    
    if not url:
        url = os.getenv("SUPABASE_URL")
        if url:
            print(f"[INFO] 从环境变量读取 URL")
    
    if not key:
        key = os.getenv("SUPABASE_KEY")
        if key:
            print(f"[INFO] 从环境变量读取 KEY")
    
    if not url or not key:
        print("[WARNING] 未提供URL或KEY，测试可能失败")
        print("使用方法:")
        print("  1. 设置环境变量: SUPABASE_URL 和 SUPABASE_KEY")
        print("  2. 或通过命令行参数: --url <URL> --key <KEY>")
        print("  3. 或直接修改脚本中的默认值")
        print("-" * 30)
    
    # 运行测试
    result = run_connectivity_tests(url, key)
    
    print("\n" + "=" * 50)
    print("测试结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 50)
    
    # 设置退出码
    sys.exit(0 if result["all_tests_passed"] else 1)