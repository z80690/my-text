# -*- coding: utf-8 -*-
"""Skills测试脚本 - 验证5个Claude Code Skills是否正常工作"""

import os
import sys
import yaml
from pathlib import Path

SKILLS_BASE = Path(r'c:\Users\Administrator\Desktop\my-text\.trae\skills')

def test_skills_exist():
    """测试1: 验证skills文件存在"""
    print("\n" + "="*60)
    print("测试1: 验证skills文件存在")
    print("="*60)

    required_skills = [
        'auto-debug/SKILL.md',
        'auto-hook/SKILL.md',
        'auto-doc/SKILL.md',
        'auto-refactor/SKILL.md',
        'local-privacy/SKILL.md'
    ]

    all_exist = True
    for skill_path in required_skills:
        full_path = SKILLS_BASE / skill_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {skill_path}")
        if not exists:
            all_exist = False

    return all_exist

def test_skills_yaml():
    """测试2: 验证skills.yaml配置"""
    print("\n" + "="*60)
    print("测试2: 验证skills.yaml配置")
    print("="*60)

    config_path = Path(r'c:\Users\Administrator\Desktop\my-text\.trae\skills.yaml')

    if not config_path.exists():
        print("  ❌ skills.yaml 不存在")
        return False

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        skills_count = len(config.get('skills', []))
        print(f"  ✅ skills.yaml 存在，包含 {skills_count} 个skills配置")

        expected_ids = ['auto-debug', 'auto-hook', 'auto-doc', 'auto-refactor', 'local-privacy']
        configured_ids = [s['skill_id'] for s in config.get('skills', [])]

        for skill_id in expected_ids:
            if skill_id in configured_ids:
                print(f"  ✅ {skill_id} 已配置")
            else:
                print(f"  ❌ {skill_id} 未配置")
                return False

        return True

    except Exception as e:
        print(f"  ❌ 读取skills.yaml失败: {e}")
        return False

def test_skill_content():
    """测试3: 验证skill内容"""
    print("\n" + "="*60)
    print("测试3: 验证skill内容完整性")
    print("="*60)

    required_skills = ['auto-debug', 'auto-hook', 'auto-doc', 'auto-refactor', 'local-privacy']

    all_valid = True
    for skill_id in required_skills:
        skill_file = SKILLS_BASE / skill_id / 'SKILL.md'

        if not skill_file.exists():
            print(f"  ❌ {skill_id}/SKILL.md 不存在")
            all_valid = False
            continue

        content = skill_file.read_text(encoding='utf-8')

        checks = [
            ('# ' in content, '标题'),
            ('功能' in content or '## 功能' in content, '功能说明'),
            ('使用' in content, '使用说明'),
        ]

        check_passed = sum(1 for c, _ in checks if c)
        print(f"  {'✅' if check_passed >= 2 else '⚠️'} {skill_id}: {check_passed}/3 项检查通过")

    return all_valid

def test_trigger_keywords():
    """测试4: 验证触发关键词"""
    print("\n" + "="*60)
    print("测试4: 验证触发关键词")
    print("="*60)

    keywords_map = {
        'auto-debug': ['调试', '报错', 'bug', '错误', '修复'],
        'auto-hook': ['hook', '钩子', '自动化', '触发'],
        'auto-doc': ['文档', 'README', '注释', '生成文档'],
        'auto-refactor': ['重构', 'refactor', '批量修改', '迁移'],
        'local-privacy': ['本地', '隐私', 'local', '笔记']
    }

    config_path = Path(r'c:\Users\Administrator\Desktop\my-text\.trae\skills.yaml')

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    configured_keywords = {s['skill_id']: s.get('trigger_keywords', []) for s in config.get('skills', [])}

    all_valid = True
    for skill_id, expected_keywords in keywords_map.items():
        configured = configured_keywords.get(skill_id, [])
        matched = sum(1 for kw in expected_keywords if kw in configured)
        print(f"  {'✅' if matched >= 2 else '⚠️'} {skill_id}: {matched}/{len(expected_keywords)} 关键词匹配")
        if matched < 2:
            all_valid = False

    return all_valid

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🚀 5个Claude Code Skills 测试")
    print("="*60)

    results = {
        'skills_exist': test_skills_exist(),
        'skills_yaml': test_skills_yaml(),
        'skill_content': test_skill_content(),
        'trigger_keywords': test_trigger_keywords()
    }

    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} {test_name}")

    print(f"\n总通过率: {passed}/{total} ({passed*100//total}%)")

    if passed == total:
        print("\n🎉 所有测试通过！5个Skills已就绪！")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查输出")
        return 1

if __name__ == '__main__':
    sys.exit(main())
