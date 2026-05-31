#!/usr/bin/env python3
"""
Skill Parser - 技能解析器
解析技能文件夹，提取技能信息
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional


class SkillParser:
    """技能解析器"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.skill_info = {}
        
    def is_valid_skill(self) -> bool:
        """检查是否为有效的技能文件夹"""
        if not self.skill_path.exists():
            return False
        
        if self.skill_path.is_file():
            return self.skill_path.name == "SKILL.md"
        
        return (self.skill_path / "SKILL.md").exists()
    
    def get_skill_root(self) -> Path:
        """获取技能根目录"""
        if self.skill_path.is_file() and self.skill_path.name == "SKILL.md":
            return self.skill_path.parent
        return self.skill_path
    
    def parse_frontmatter(self, content: str) -> Dict:
        """解析 Markdown frontmatter"""
        frontmatter = {}
        pattern = r'^---\n(.*?)\n---'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1))
            except:
                pass
        
        return frontmatter
    
    def parse_skill(self) -> Dict:
        """解析技能信息"""
        skill_root = self.get_skill_root()
        skill_md = skill_root / "SKILL.md"
        
        if not skill_md.exists():
            return {}
        
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter = self.parse_frontmatter(content)
        
        self.skill_info = {
            "name": frontmatter.get("name", skill_root.name),
            "description": frontmatter.get("description", ""),
            "version": frontmatter.get("version", ""),
            "path": str(skill_root),
            "files": self.list_files(skill_root),
            "config": self.parse_config(skill_root),
            "examples": self.list_examples(skill_root)
        }
        
        return self.skill_info
    
    def list_files(self, root: Path, depth: int = 2) -> List[str]:
        """列出技能文件夹中的文件"""
        files = []
        for item in root.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                files.append(item.name)
            elif item.is_dir() and not item.name.startswith('.') and depth > 0:
                files.append(f"{item.name}/")
                files.extend([f"{item.name}/{f}" for f in self.list_files(item, depth - 1)])
        return sorted(files)
    
    def parse_config(self, root: Path) -> Dict:
        """解析配置文件"""
        config = {}
        config_dir = root / "config"
        
        if config_dir.exists():
            for cfg_file in config_dir.iterdir():
                if cfg_file.suffix in ['.yaml', '.yml', '.json']:
                    try:
                        with open(cfg_file, 'r', encoding='utf-8') as f:
                            if cfg_file.suffix in ['.yaml', '.yml']:
                                config[cfg_file.name] = yaml.safe_load(f)
                            else:
                                import json
                                config[cfg_file.name] = json.load(f)
                    except:
                        pass
        
        return config
    
    def list_examples(self, root: Path) -> List[str]:
        """列出示例文件"""
        examples = []
        examples_dir = root / "examples"
        
        if examples_dir.exists():
            for example_file in examples_dir.iterdir():
                if example_file.is_file():
                    examples.append(example_file.name)
        
        return examples
    
    def format_skill_card(self) -> str:
        """格式化技能卡片"""
        if not self.skill_info:
            return "❌ 无法解析技能信息"
        
        card = f"""
✅ 检测到技能: {self.skill_info['name']}

📦 技能信息:
名称: {self.skill_info['name']}
描述: {self.skill_info['description']}
"""
        
        if self.skill_info.get('version'):
            card += f"版本: {self.skill_info['version']}\n"
        
        card += f"\n📁 文件结构:\n"
        for f in self.skill_info.get('files', [])[:10]:
            card += f"  - {f}\n"
        
        if len(self.skill_info.get('files', [])) > 10:
            card += f"  ... (还有 {len(self.skill_info['files']) - 10} 个文件)\n"
        
        card += """
你想用这个技能做什么？
1. 调用技能执行任务
2. 查看技能详细文档
3. 查看技能示例代码
4. 查看技能配置文件
5. 其他（告诉我你想做什么）
"""
        
        return card


def main():
    """主函数（演示用）"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python skill-parser.py <技能路径>")
        return
    
    parser = SkillParser(sys.argv[1])
    
    if not parser.is_valid_skill():
        print("❌ 不是有效的技能文件夹或 SKILL.md 文件")
        return
    
    info = parser.parse_skill()
    print(parser.format_skill_card())


if __name__ == "__main__":
    main()
