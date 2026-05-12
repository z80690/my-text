import asyncio
import sys
sys.path.insert(0, '.trae/skills')

from manager import SkillManager

async def test_dynamic_loading():
    """Test dynamic skill loading"""
    print('=' * 70)
    print('TEST 1: 动态加载技能管理器初始化')
    print('=' * 70)
    
    manager = SkillManager()
    await manager.initialize()
    
    skill_ids = manager.get_skill_ids()
    print('')
    print('已加载的技能列表:')
    print('-' * 50)
    for skill_id in skill_ids:
        skill = manager.get(skill_id)
        print(f'  [{skill_id}]')
        print(f'    名称: {skill.get("name", "未知")}')
        print(f'    版本: {skill.get("version", "1.0")}')
        if skill.get('trigger_keywords'):
            print(f'    触发关键词: {", ".join(skill["trigger_keywords"])}')
        print('')
    
    print(f'总技能数: {len(skill_ids)}')
    print('')
    
    return manager

async def test_skill_search(manager):
    """Test skill search functionality"""
    print('=' * 70)
    print('TEST 2: 技能搜索与匹配')
    print('=' * 70)
    
    test_queries = [
        '代码审查',
        'API Token优化',
        '清理未使用的文件',
        '设计界面',
        '代码重构'
    ]
    
    print('测试搜索查询:')
    print('-' * 50)
    
    for query in test_queries:
        matched = []
        for skill_id in manager.get_skill_ids():
            skill = manager.get(skill_id)
            keywords = skill.get('trigger_keywords', [])
            description = skill.get('description', '')
            
            # 检查关键词匹配
            if any(keyword in query for keyword in keywords):
                matched.append(skill_id)
            # 检查描述匹配
            elif query in description:
                matched.append(skill_id)
        
        if matched:
            print(f' 查询 "{query}" 匹配到: {", ".join(matched)}')
        else:
            print(f' 查询 "{query}" 未匹配到任何技能')
    
    print('')

async def test_skill_reload(manager):
    """Test skill reload functionality"""
    print('=' * 70)
    print('TEST 3: 技能热重载')
    print('=' * 70)
    
    initial_count = len(manager.get_skill_ids())
    print(f'初始技能数量: {initial_count}')
    
    await manager.reload()
    
    reloaded_count = len(manager.get_skill_ids())
    print(f'重载后技能数量: {reloaded_count}')
    
    if initial_count == reloaded_count:
        print('✓ 重载成功，技能数量保持一致')
    else:
        print(f'! 重载后技能数量变化: {initial_count} -> {reloaded_count}')
    
    print('')

async def test_skill_details(manager):
    """Test getting detailed skill information"""
    print('=' * 70)
    print('TEST 4: 获取技能详细信息')
    print('=' * 70)
    
    sample_skills = ['my-code-review', 'file-cleaner', 'api-token-optimizer']
    
    for skill_id in sample_skills:
        skill = manager.get(skill_id)
        if skill:
            print(f'技能ID: {skill_id}')
            print(f'  名称: {skill.get("name")}')
            print(f'  描述: {skill.get("description")}')
            print(f'  版本: {skill.get("version")}')
            print(f'  作者: {skill.get("author")}')
            print(f'  定义文件: {skill.get("definition_file")}')
            print(f'  触发关键词: {skill.get("trigger_keywords", [])}')
            print('')
        else:
            print(f'技能 {skill_id} 未找到')
            print('')

async def test_error_handling(manager):
    """Test error handling for missing skills"""
    print('=' * 70)
    print('TEST 5: 错误处理 - 获取不存在的技能')
    print('=' * 70)
    
    non_existent_skill = manager.get('non-existent-skill-id-12345')
    
    if non_existent_skill is None:
        print('✓ 获取不存在的技能返回 None，错误处理正常')
    else:
        print('! 获取不存在的技能没有返回 None')
    
    print('')

async def main():
    """Run all tests"""
    print('')
    print('╔══════════════════════════════════════════════════════════════════╗')
    print('║              技能动态加载功能测试套件                              ║')
    print('╚══════════════════════════════════════════════════════════════════╝')
    print('')
    
    # Test 1: Dynamic Loading
    manager = await test_dynamic_loading()
    
    # Test 2: Search
    await test_skill_search(manager)
    
    # Test 3: Reload
    await test_skill_reload(manager)
    
    # Test 4: Details
    await test_skill_details(manager)
    
    # Test 5: Error Handling
    await test_error_handling(manager)
    
    print('=' * 70)
    print('测试完成!')
    print('=' * 70)

if __name__ == '__main__':
    asyncio.run(main())
