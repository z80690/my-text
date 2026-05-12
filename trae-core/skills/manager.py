# -*- coding: utf-8 -*-
"""技能管理器 - 自动启用"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

class SkillManager:
    """技能管理器"""
    
    def __init__(self):
        self.skills: Dict[str, Any] = {}
    
    async def initialize(self):
        """初始化技能管理器"""
        config_path = Path('.trae/skills.yaml')
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
                for skill_data in config.get('skills', []):
                    self.skills[skill_data['skill_id']] = skill_data
    
    def get(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """获取技能"""
        return self.skills.get(skill_id)
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有技能"""
        return list(self.skills.values())
    
    def get_skill_ids(self) -> List[str]:
        """获取所有技能ID"""
        return list(self.skills.keys())
