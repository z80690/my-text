# -*- coding: utf-8 -*-
"""简单测试"""

import sys
import traceback

try:
    print("导入模块...")
    sys.path.insert(0, r"c:\Users\Administrator\Desktop\my-text\trae-core")
    
    from agents.base import AgentConfig
    print("✅ 导入 AgentConfig")
    
    from agents.implementations_v2 import DispatcherAgent
    print("✅ 导入 DispatcherAgent")
    
    print("\n创建配置...")
    config = AgentConfig(id="dispatcher", name="test", type="coordinator", capabilities=[])
    print("✅ 创建配置成功")
    
    print("\n创建调度器...")
    dispatcher = DispatcherAgent(config)
    print("✅ 创建调度器成功")
    
    print("\n执行任务...")
    result = dispatcher._default_execute("测试任务", {})
    print("✅ 执行成功")
    print(f"结果: {result}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    traceback.print_exc()
    sys.exit(1)
