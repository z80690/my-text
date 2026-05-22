# -*- coding: utf-8 -*-
"""
registry.py 修复补丁
添加对所有 *.md 文件的扫描支持
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional

# 读取原始 registry.py
with open(r"c:\Users\Administrator\Desktop\my-text\.trae\agents\registry.py", "r", encoding="utf-8") as f:
    content = f.read()

# 查找并替换 _scan_agent_markdowns 方法
old_method = '''    def _scan_agent_markdowns(self):
        """扫描智能体markdown文件"""
        agents_path = self._base_path / "agents"
        if not agents_path.exists():
            return
        
        for md_file in agents_path.glob("*_agent.md"):
            agent_data = self._parse_agent_markdown(md_file)
            if agent_data:
                agent_id = agent_data['id']
                self._agents[agent_id] = agent_data
                print(f"  [+] 解析智能体: {agent_data['name']} ({agent_id})")

        for md_file in agents_path.glob("*-agent.md"):
            agent_data = self._parse_agent_markdown(md_file)
            if agent_data:
                agent_id = agent_data['id']
                if agent_id not in self._agents:
                    self._agents[agent_id] = agent_data
                    print(f"  [+] 解析智能体: {agent_data['name']} ({agent_id})")'''

new_method = '''    def _scan_agent_markdowns(self):
        """扫描智能体markdown文件"""
        agents_path = self._base_path / "agents"
        if not agents_path.exists():
            return
        
        # 扫描所有 *.md 文件（排除已处理的）
        for md_file in agents_path.glob("*.md"):
            agent_data = self._parse_agent_markdown(md_file)
            if agent_data:
                agent_id = agent_data['id']
                if agent_id not in self._agents:
                    self._agents[agent_id] = agent_data
                    print(f"  [+] 解析智能体: {agent_data['name']} ({agent_id})")'''

# 替换
new_content = content.replace(old_method, new_method)

# 写回
with open(r"c:\Users\Administrator\Desktop\my-text\.trae\agents\registry.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ registry.py 修复完成")
