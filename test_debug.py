import sys
import os

print('Python version:', sys.version)
print('Current directory:', os.getcwd())

# 使用绝对路径
skills_path = os.path.join(os.getcwd(), '.trae/skills')
print('Skills path:', skills_path)

sys.path.insert(0, skills_path)

try:
    from manager import SkillManager
    print('Import successful')
    
    # 测试创建实例
    manager = SkillManager()
    print('SkillManager instance created')
    
except Exception as e:
    print('Error:', str(e))
    import traceback
    traceback.print_exc()
