"""
测试: AI自动记忆处理
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from auto_memory_handler import AutoMemoryHandler, auto_process

print('=== 模拟AI自动记忆处理 ===')
print()

# 用户消息1
msg1 = '我习惯用4空格缩进'
result1 = auto_process(msg1)
print(f'用户: {msg1}')
print(f'AI自动处理: {result1}')
print()

# 用户消息2
msg2 = '以后只要纯代码，不要解释注释'
result2 = auto_process(msg2)
print(f'用户: {msg2}')
print(f'AI自动处理: {result2}')
print()

# 用户消息3
msg3 = '这是电商后台系统，2024年3月启动'
result3 = auto_process(msg3)
print(f'用户: {msg3}')
print(f'AI自动处理: {result3}')
print()

# 用户消息4 (明知识，不应该记忆)
msg4 = '这个项目用的是React 18.2.0'
result4 = auto_process(msg4)
print(f'用户: {msg4}')
print(f'AI自动处理: {result4}')
print()

print('=== 验证记忆文件 ===')
for root, dirs, files in os.walk('.trae/memories'):
    for f in files:
        if f.endswith('.md') and not f.startswith('dream'):
            print(os.path.join(root, f))
