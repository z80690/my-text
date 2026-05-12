# -*- coding: utf-8 -*-
"""Skill Manager - Dynamic Loading"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional

class SkillManager:
    """Skill Manager - Dynamically scan skills folder"""

    def __init__(self):
        self.skills: Dict[str, Any] = {}
        self.skills_dir = Path('.trae/skills')

    async def initialize(self):
        """Initialize skill manager - Dynamically scan skills folder"""
        self.skills = {}

        if not self.skills_dir.exists():
            print('WARNING: Skills directory not found: ' + str(self.skills_dir))
            return

        print('Scanning skills directory: ' + str(self.skills_dir))

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_id = skill_dir.name
            skill_md_path = skill_dir / 'SKILL.md'

            if not skill_md_path.exists():
                continue

            skill_data = await self._parse_skill_md(skill_md_path, skill_id)
            if skill_data:
                self.skills[skill_id] = skill_data
                print('  Loaded skill: ' + skill_id)

        print('Dynamic loading complete, total ' + str(len(self.skills)) + ' skills loaded')

    async def _parse_skill_md(self, md_path: Path, skill_id: str) -> Optional[Dict[str, Any]]:
        """Parse SKILL.md file"""
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            skill_data = {
                'skill_id': skill_id,
                'definition_file': str(md_path),
                'name': self._extract_yaml_field(content, 'name'),
                'description': self._extract_yaml_field(content, 'description'),
                'trigger_keywords': self._extract_keywords(content),
                'version': self._extract_yaml_field(content, 'version', '1.0'),
                'author': self._extract_yaml_field(content, 'author', 'Unknown')
            }

            return skill_data

        except Exception as e:
            print('  Failed to parse ' + skill_id + ': ' + str(e))
            return None

    def _extract_yaml_field(self, content: str, field: str, default: str = '') -> str:
        """Extract field from YAML front matter"""
        pattern = r'^---\s*\n' + field + r':\s*"?(.+?)"?\s*\n---'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        
        if match:
            value = match.group(1).strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return value
        
        return default

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract trigger keywords"""
        keywords = []

        pattern = r'^\*\*触发关键词\*\*[:：:]\s*(.+)$'
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)

        if match:
            keywords_str = match.group(1)
            keywords = [kw.strip() for kw in keywords_str.split('、')]

        return keywords

    def get(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Get skill by ID"""
        return self.skills.get(skill_id)

    def list_skills(self) -> List[Dict[str, Any]]:
        """List all skills"""
        return list(self.skills.values())

    def get_skill_ids(self) -> List[str]:
        """Get all skill IDs"""
        return list(self.skills.keys())

    async def reload(self):
        """Reload all skills"""
        print('Reloading skills...')
        await self.initialize()

    async def add_skill(self, skill_id: str, skill_data: Dict[str, Any]):
        """Add new skill"""
        self.skills[skill_id] = skill_data
        print('  Added skill: ' + skill_id)

    async def remove_skill(self, skill_id: str):
        """Remove skill"""
        if skill_id in self.skills:
            del self.skills[skill_id]
            print('  Removed skill: ' + skill_id)
