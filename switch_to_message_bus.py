# -*- coding: utf-8 -*-
"""
切换到消息总线模式（异步模式）
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trae-core'))

from agents.implementations_v2 import DispatcherAgent
from agents.base import AgentConfig

def main():
    print("="*60)
    print("🚀 切换到消息总线模式")
    print("="*60)
    
    # 创建调度器配置
    config = AgentConfig(
        agent_id="dispatcher_agent",
        name="调度智能体",
        description="智能体团队调度员",
        config={}
    )
    
    # 创建调度器实例
    dispatcher = DispatcherAgent(config)
    
    # 显示当前模式
    current_mode = dispatcher.get_execution_mode()
    print(f"\n当前执行模式: {current_mode}")
    print(f"消息总线状态: {'✅ 已连接' if dispatcher._message_bus else '❌ 未连接'}")
    
    # 切换到异步模式（消息总线模式）
    print("\n🔄 正在切换到消息总线模式...")
    success = dispatcher.set_execution_mode("async")
    
    if success:
        new_mode = dispatcher.get_execution_mode()
        print(f"✅ 切换成功！")
        print(f"   当前模式: {new_mode}")
        
        # 检查消息总线端点
        if dispatcher._message_bus:
            endpoints = list(dispatcher._message_bus._endpoints.keys())
            print(f"   已注册端点: {len(endpoints)} 个")
            print(f"   端点列表: {endpoints}")
    else:
        print("❌ 切换失败！")
    
    print("\n" + "="*60)
    print("📊 切换完成")
    print("="*60)

if __name__ == "__main__":
    main()