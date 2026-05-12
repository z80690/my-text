# -*- coding: utf-8 -*-
"""Git 同步脚本 - 同步所有 Skills 相关文件到 GitHub"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent

def run_git_command(args, cwd=None):
    """运行 Git 命令"""
    cmd = ['git'] + args
    print(f"▶️  执行: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    
    if result.stdout:
        print(f"📤 输出:\n{result.stdout}")
    if result.stderr and 'warning' not in result.stderr.lower() and 'Everything up-to-date' not in result.stderr:
        print(f"⚠️  警告:\n{result.stderr}")
    
    return result

def main():
    print("="*60)
    print("🚀 Git 同步 - Skills 自动化系统")
    print("="*60)

    # 1. 添加文件
    print("\n📝 步骤1: 添加文件...")
    files_to_add = [
        # Skills 核心文件
        '.trae/skills/auto-debug/SKILL.md',
        '.trae/skills/auto-hook/SKILL.md',
        '.trae/skills/auto-doc/SKILL.md',
        '.trae/skills/auto-refactor/SKILL.md',
        '.trae/skills/local-privacy/SKILL.md',
        '.trae/skills.yaml',
        
        # 文档
        '.trae/TRIGGER_KEYWORDS.md',
        '.trae/SKILLS_AUTO_GUIDE.md',
        
        # 测试脚本
        '.trae/test_skills.py',
        
        # 自动化系统
        '.trae/skill_auto_integration.py',
        '.trae/skill_runner.py',
        '.trae/auto_hook_system.py',
        '.trae/hooks/hook_config.json',
        
        # 日志（示例）
        '.trae/logs/skill_executions_2026-05-11.json',
        '.trae/logs/auto_events_2026-05-11.md',
    ]
    
    existing_files = [f for f in files_to_add if (REPO_ROOT / f).exists()]
    run_git_command(['add'] + existing_files)

    # 2. 提交
    print("\n💾 步骤2: 提交更改...")
    commit_msg = f"完善 Skills 自动化系统 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    run_git_command(['commit', '-m', commit_msg])

    # 3. 推送
    print("\n☁️  步骤3: 推送到 GitHub...")
    result = run_git_command(['push', 'origin', 'main'])
    
    if result.returncode == 0:
        print("\n✅ 同步成功！")
        print(f"\n📦 已同步文件数: {len(existing_files)}")
        return 0
    else:
        print("\n❌ 同步失败，请检查 Git 配置")
        return 1

if __name__ == '__main__':
    sys.exit(main())
