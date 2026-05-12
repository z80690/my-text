import asyncio
import sys
sys.path.insert(0, '.trae/skills')
from manager import SkillManager

async def test():
    manager = SkillManager()
    await manager.initialize()
    
    print('')
    print('=' * 60)
    print('Loaded skills list:')
    print('=' * 60)
    for skill_id in manager.get_skill_ids():
        skill = manager.get(skill_id)
        print('  - ' + skill_id + ': ' + skill.get('name', 'Unknown'))
        if skill.get('trigger_keywords'):
            print('    Keywords: ' + str(skill['trigger_keywords']))
    print('=' * 60)
    print('Total: ' + str(len(manager.get_skill_ids())) + ' skills')

if __name__ == '__main__':
    asyncio.run(test())
