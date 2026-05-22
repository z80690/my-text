# -*- coding: utf-8 -*-
"""
智能体文件标准化脚本
1. 批量重命名 .trae/agents/*.md 文件为标准格式（小写+横杠）
2. 检查并修复 YAML 头部格式
3. 生成修改报告
"""

import os
import re
from pathlib import Path
import shutil

# 项目根目录
PROJECT_ROOT = Path(r"c:\Users\Administrator\Desktop\my-text")
AGENTS_DIR = PROJECT_ROOT / ".trae" / "agents"

# 标准格式映射表（当前文件名 → 标准文件名）
RENAME_MAP = {
    "assistant_通用助手_agent.md": "assistant-agent.md",
    "base_基础智能体_agent.md": "base-agent.md",
    "chess_国际象棋_agent.md": "chess-agent.md",
    "closure_闭包智能体_agent.md": "closure-agent.md",
    "code_executor_代码执行_agent.md": "code-executor.md",
    "dispatcher_agent.md": "dispatcher-agent.md",
    "dispatcher_智能体团队调度员_agent.md": "dispatcher-agent.md",
    "dspy_DSPy_agent.md": "dspy-agent.md",
    "editor_编辑器_agent.md": "editor-agent.md",
    "fastapi_FastAPI_agent.md": "fastapi-agent.md",
    "graphrag_GraphRAG_agent.md": "graphrag-agent.md",
    "grpc_gRPC_agent.md": "grpc-agent.md",
    "message_filter_消息过滤_agent.md": "message-filter.md",
    "monitor_监控智能体_agent.md": "monitor-agent.md",
    "nuwa_女娲造人_agent.md": "nuwa-agent.md",
    "routed_路由智能体_agent.md": "routed-agent.md",
    "rule_interpreter_规则解释_agent.md": "rule-interpreter.md",
    "semantic_router_agent.md": "semantic-router-agent.md",
    "semantic_router_语义路由_agent.md": "semantic-router-agent.md",
    "society_of_mind_心智社会_agent.md": "society-of-mind-agent.md",
    "streamlit_Streamlit_agent.md": "streamlit-agent.md",
    "teachable_可教学_agent.md": "teachable-agent.md",
    "tool_工具智能体_agent.md": "tool-agent.md",
    "user_proxy_用户代理_agent.md": "user-proxy-agent.md",
    "writer_作家_agent.md": "writer-agent.md",
    "xlang_跨语言_agent.md": "xlang-agent.md",
}

# YAML 模板
YAML_TEMPLATE = """---
name: {name}
description: {description}
tools: Read, Glob, Grep, Bash
---

"""

def extract_name_from_content(file_path):
    """从文件内容中提取智能体名称"""
    try:
        content = file_path.read_text(encoding='utf-8')
        name_match = re.search(r'\*\*名称 / Name\*\*:\s*([^\n]+)', content)
        if name_match:
            return name_match.group(1).strip()
    except Exception as e:
        print(f"  ⚠️ 读取文件失败: {e}")
    return None

def fix_yaml_header(file_path, new_name):
    """修复 YAML 头部"""
    try:
        content = file_path.read_text(encoding='utf-8')

        # 提取描述
        desc_match = re.search(r'\*\*描述 / Description\*\*:\s*([^\n]+)', content)
        description = desc_match.group(1).strip() if desc_match else new_name

        # 跳过已有的标准格式
        if content.startswith('---'):
            yaml_match = re.match(r'^---\nname: (.+)\ndescription: (.+)\ntools: (.+)\n---', content)
            if yaml_match:
                print(f"  ✅ YAML格式已标准，跳过")
                return False

        # 找到 markdown 内容开始位置（第一个 # 标题）
        header_end = content.find('# ')
        if header_end == -1:
            header_end = len(content)

        # 提取 markdown 内容
        md_content = content[header_end:].strip()

        # 生成新的标准格式
        new_yaml = YAML_TEMPLATE.format(
            name=new_name,
            description=description
        )

        # 组合新内容
        new_content = new_yaml + md_content

        # 写回文件
        file_path.write_text(new_content, encoding='utf-8')
        print(f"  ✅ YAML头部已修复")
        return True

    except Exception as e:
        print(f"  ❌ 修复YAML失败: {e}")
        return False

def process_agents_directory():
    """处理 agents 目录"""
    print("=" * 70)
    print("智能体文件标准化脚本")
    print("=" * 70)

    if not AGENTS_DIR.exists():
        print(f"❌ 目录不存在: {AGENTS_DIR}")
        return

    # 备份目录
    backup_dir = AGENTS_DIR.parent / "agents_backup"
    print(f"\n📦 创建备份目录: {backup_dir}")
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    shutil.copytree(AGENTS_DIR, backup_dir)
    print("✅ 备份完成")

    # 统计
    total = 0
    renamed = 0
    yaml_fixed = 0
    errors = []

    # 步骤1: 重命名文件
    print("\n" + "=" * 70)
    print("步骤1: 重命名文件")
    print("=" * 70)

    md_files = list(AGENTS_DIR.glob("*.md"))

    for md_file in md_files:
        total += 1
        old_name = md_file.name

        if old_name in RENAME_MAP:
            new_name = RENAME_MAP[old_name]
            new_path = AGENTS_DIR / new_name

            try:
                # 重命名
                shutil.move(str(md_file), str(new_path))
                print(f"✅ {old_name} → {new_name}")
                renamed += 1

                # 修复YAML
                print(f"   修复YAML头部...")
                if fix_yaml_header(new_path, new_name.replace('.md', '')):
                    yaml_fixed += 1

            except Exception as e:
                print(f"❌ 重命名失败: {e}")
                errors.append(f"{old_name}: {e}")
        else:
            # 检查是否已经是标准格式
            if re.match(r'^[a-z0-9]+(-[a-z0-9]+)*\.md$', old_name):
                print(f"⏭️  {old_name} 已是标准格式，跳过")
            else:
                print(f"⚠️  {old_name} - 未在映射表中")

    # 步骤2: 验证结果
    print("\n" + "=" * 70)
    print("步骤2: 验证结果")
    print("=" * 70)

    final_files = list(AGENTS_DIR.glob("*.md"))
    print(f"\n📊 最终文件列表 ({len(final_files)} 个 .md 文件):")
    print("-" * 70)

    for f in sorted(final_files):
        # 检查格式
        is_standard = bool(re.match(r'^[a-z0-9]+(-[a-z0-9]+)*\.md$', f.name))
        status = "✅" if is_standard else "❌"
        print(f"  {status} {f.name}")

    # 步骤3: 生成报告
    print("\n" + "=" * 70)
    print("步骤3: 执行报告")
    print("=" * 70)
    print(f"  📁 处理文件总数: {total}")
    print(f"  ✅ 成功重命名: {renamed}")
    print(f"  🔧 修复YAML头部: {yaml_fixed}")
    print(f"  ❌ 错误: {len(errors)}")

    if errors:
        print("\n  错误详情:")
        for err in errors:
            print(f"    - {err}")

    # 备份恢复说明
    print("\n" + "=" * 70)
    print("⚠️  重要提示")
    print("=" * 70)
    print(f"  原始文件已备份到: {backup_dir}")
    print(f"  如果需要恢复，运行:")
    print(f"  shutil.rmtree('{AGENTS_DIR}')")
    print(f"  shutil.copytree('{backup_dir}', '{AGENTS_DIR}')")

    print("\n✅ 标准化完成！")
    print("\n📋 下一步:")
    print("  1. 在Trae中运行 /agents reload")
    print("  2. 运行 /agents list 查看智能体")
    print("  3. 给每个智能体开启「可被其他智能体调用」权限")
    print("  4. 给调度智能体开启「允许调用其他智能体」权限")

if __name__ == "__main__":
    process_agents_directory()
