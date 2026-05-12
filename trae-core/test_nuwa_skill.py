# -*- coding: utf-8 -*-
"""
测试 Nuwa Skill 是否正确安装
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_nuwa_skill():
    try:
        # 测试1: 加载技能管理器
        from skills.manager import SkillManager
        
        skill_manager = SkillManager()
        await skill_manager.initialize()
        
        skills = skill_manager.list_skills()
        skill_ids = skill_manager.get_skill_ids()
        
        print(f"测试1: 技能管理器加载成功")
        print(f"已加载技能数量: {len(skills)}")
        print(f"技能列表: {skill_ids}")
        print()
        
        # 测试2: 检查 nuwa_skill 是否在列表中
        if 'nuwa_skill' in skill_ids:
            print("测试2: nuwa_skill 已成功注册 ✓")
            nuwa_skill = skill_manager.get('nuwa_skill')
            print(f"  技能名称: {nuwa_skill.get('name')}")
            print(f"  英文名称: {nuwa_skill.get('name_en')}")
            print(f"  版本: {nuwa_skill.get('version')}")
            print(f"  状态: {nuwa_skill.get('status')}")
            print(f"  描述: {nuwa_skill.get('description')}")
        else:
            print("测试2: nuwa_skill 未注册 ✗")
            return False
        
        # 测试3: 检查 SKILL.md 文件是否存在
        import yaml
        with open('.trae/skills.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        nuwa_config = None
        for skill in config.get('skills', []):
            if skill['skill_id'] == 'nuwa_skill':
                nuwa_config = skill
                break
        
        if nuwa_config:
            print("\n测试3: skills.yaml 配置正确 ✓")
            print(f"  definition_file: {nuwa_config.get('definition_file')}")
            
            # 检查文件是否存在
            definition_path = nuwa_config.get('definition_file')
            if os.path.exists(definition_path):
                print(f"  SKILL.md 文件存在: {definition_path} ✓")
            else:
                print(f"  SKILL.md 文件不存在: {definition_path} ✗")
                return False
        else:
            print("测试3: skills.yaml 中未找到 nuwa_skill 配置 ✗")
            return False
        
        # 测试4: 检查技能目录结构
        nuwa_dir = '.trae/skills/nuwa-skill'
        if os.path.isdir(nuwa_dir):
            print("\n测试4: 技能目录存在 ✓")
            contents = os.listdir(nuwa_dir)
            print(f"  目录内容: {contents}")
            
            # 检查关键文件
            key_files = ['SKILL.md', 'README.md', 'examples/', 'references/']
            for file in key_files:
                if os.path.exists(os.path.join(nuwa_dir, file)):
                    print(f"    ✓ {file}")
                else:
                    print(f"    ✗ {file}")
        else:
            print("测试4: 技能目录不存在 ✗")
            return False
        
        print("\n=== 所有测试通过 ===")
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import asyncio
    success = asyncio.run(test_nuwa_skill())
    sys.exit(0 if success else 1)
