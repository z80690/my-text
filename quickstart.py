# -*- coding: utf8 -*-
"""
快速启动指南 - 智谱AI集成

本文件提供快速启动和测试智谱AI集成的步骤
"""

import os
import subprocess
import sys


def print_header(title: str):
    """打印标题"""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def check_env_file():
    """检查.env文件是否存在"""
    if not os.path.exists(".env"):
        print("[ERROR] .env文件不存在！")
        print("请复制.env.example为.env并填写配置")
        return False

    print("[✓] .env文件已存在")
    return True


def check_zhipu_config():
    """检查智谱AI配置"""
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("ZHIPU_API_KEY")
    model = os.getenv("ZHIPU_MODEL")

    if not api_key or api_key == "your-zhipu-api-key-here":
        print("[ERROR] 智谱AI API密钥未配置")
        return False

    if not model:
        print("[WARNING] 智谱AI模型未配置，使用默认模型glm-4")

    print(f"[✓] 智谱AI配置: 模型={model}")
    return True


def check_encryption_key():
    """检查加密密钥配置"""
    from dotenv import load_dotenv

    load_dotenv()

    encryption_key = os.getenv("ENCRYPTION_KEY")

    if not encryption_key or encryption_key == "your-encryption-key-here":
        print("[WARNING] 加密密钥未配置，将无法使用加密功能")
        return False

    print("[✓] 加密密钥已配置")
    return True


def install_dependencies():
    """安装依赖"""
    print()
    print("安装Python依赖...")
    print("-" * 70)

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "src/requirements.txt"],
            check=True,
            capture_output=False
        )
        print()
        print("[✓] 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 依赖安装失败: {e}")
        return False


def run_zhipu_tests():
    """运行智谱AI测试"""
    print()
    print("运行智谱AI集成测试...")
    print("-" * 70)

    try:
        result = subprocess.run(
            [sys.executable, "src/test_zhipu_ai.py"],
            cwd=os.getcwd(),
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] 测试运行失败: {e}")
        return False


def main():
    """主函数"""
    print_header("智谱AI集成快速启动指南")

    steps = [
        ("检查配置文件", check_env_file),
        ("检查智谱AI配置", check_zhipu_config),
        ("检查加密密钥", check_encryption_key),
        ("安装依赖", install_dependencies),
        ("运行测试", run_zhipu_tests)
    ]

    all_passed = True

    for step_name, step_func in steps:
        print()
        print(f"步骤: {step_name}")
        print("-" * 70)

        if not step_func():
            all_passed = False
            break

    print()
    print_header("总结")

    if all_passed:
        print("[✓] 所有步骤完成！智谱AI已成功集成")
        print()
        print("可用的API端点:")
        print("  - POST /api/ai/generate  - 文本生成")
        print("  - POST /api/ai/chat     - 对话补全")
        print()
        print("使用方法:")
        print("  1. 启动服务: python -m uvicorn src.main:app --port 9000")
        print("  2. 测试API: curl -X POST http://localhost:9000/api/ai/generate \\")
        print("              -H 'Content-Type: application/json' \\")
        print("              -d '{\"prompt\": \"你好\"}'")
    else:
        print("[!] 部分步骤未完成，请检查错误信息")
        print()
        print("需要帮助？请查看文档或联系开发团队")


if __name__ == "__main__":
    main()
