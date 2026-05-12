#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步工具 - 保持Markdown规则文件与YAML配置文件同步

功能：
1. 从Markdown文件提取元数据更新YAML配置
2. 从YAML配置生成/更新Markdown文件
3. 监听文件变化自动同步
"""

import os
import re
import yaml
import json
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 配置
CONFIG_PATH = Path(".trae")
AGENTS_MD_DIR = CONFIG_PATH / "agents"
SKILLS_MD_DIR = CONFIG_PATH / "skills"
RULES_MD_DIR = CONFIG_PATH / "rules"

AGENTS_YAML = CONFIG_PATH / "agents.yaml"
SKILLS_YAML = CONFIG_PATH / "skills.yaml"
WORKFLOWS_YAML = CONFIG_PATH / "workflows.yaml"

class SyncEventHandler(FileSystemEventHandler):
    """文件变更事件处理器"""
    
    def on_modified(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            
            # 处理智能体文件变更
            if AGENTS_MD_DIR in file_path.parents:
                if file_path.suffix == ".md":
                    print(f"检测到智能体文件变更: {file_path}")
                    sync_agents_md_to_yaml()
            
            # 处理技能文件变更
            elif SKILLS_MD_DIR in file_path.parents:
                if file_path.suffix == ".md":
                    print(f"检测到技能文件变更: {file_path}")
                    sync_skills_md_to_yaml()
            
            # 处理规则文件变更
            elif RULES_MD_DIR in file_path.parents:
                if file_path.suffix == ".md":
                    print(f"检测到规则文件变更: {file_path}")
                    # 根据文件名判断需要同步的YAML
                    if "workflow" in file_path.stem.lower():
                        sync_workflows_md_to_yaml()

def load_yaml(file_path: Path) -> dict:
    """加载YAML文件"""
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

def save_yaml(file_path: Path, data: dict):
    """保存YAML文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def extract_metadata_from_md(content: str) -> dict:
    """从Markdown内容提取元数据"""
    metadata = {}
    
    # 提取YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1])
            except:
                pass
    
    # 提取能力列表
    cap_match = re.search(r'##\s*能力\s*\n((?:\s*-\s*.+\n?)+)', content)
    if cap_match:
        capabilities = [line.strip('- ').strip() for line in cap_match.group(1).strip().split('\n') if line.strip()]
        metadata['capabilities'] = capabilities
    
    # 提取描述
    desc_match = re.search(r'##\s*描述\s*\n(.+?)(?=\n##|$)', content, re.DOTALL)
    if desc_match:
        metadata['description'] = desc_match.group(1).strip()
    
    return metadata

def parse_agent_filename(filename: str) -> tuple:
    """解析智能体文件名: {agent_id}_{中文名称}_agent.md"""
    stem = filename.replace('.md', '')
    parts = stem.split('_')
    
    if len(parts) >= 3 and parts[-1] == 'agent':
        agent_id = parts[0]
        chinese_name = '_'.join(parts[1:-1]) if len(parts) > 2 else ""
        return agent_id, chinese_name
    
    return None, None

def sync_agents_md_to_yaml():
    """同步智能体Markdown文件到YAML配置"""
    yaml_data = load_yaml(AGENTS_YAML)
    agents = yaml_data.get('agents', [])
    
    # 创建智能体ID到配置的映射
    agent_map = {agent['id']: agent for agent in agents}
    
    # 扫描所有智能体Markdown文件
    for md_file in AGENTS_MD_DIR.glob('*_agent.md'):
        agent_id, chinese_name = parse_agent_filename(md_file.name)
        
        if not agent_id:
            continue
        
        # 读取文件内容
        content = md_file.read_text(encoding='utf-8')
        metadata = extract_metadata_from_md(content)
        
        # 更新或创建智能体配置
        if agent_id in agent_map:
            agent_map[agent_id]['name'] = chinese_name
            agent_map[agent_id]['description'] = metadata.get('description', agent_map[agent_id].get('description', ''))
            agent_map[agent_id]['capabilities'] = metadata.get('capabilities', agent_map[agent_id].get('capabilities', []))
            agent_map[agent_id]['qos_level'] = metadata.get('qos_level', agent_map[agent_id].get('qos_level', 'normal'))
            agent_map[agent_id]['version'] = metadata.get('version', agent_map[agent_id].get('version', '1.0.0'))
            agent_map[agent_id]['file_path'] = str(md_file)
            agent_map[agent_id]['status'] = 'active'
        else:
            agent_map[agent_id] = {
                'id': agent_id,
                'name': chinese_name,
                'name_en': metadata.get('name_en', f"{agent_id} Agent"),
                'description': metadata.get('description', ''),
                'capabilities': metadata.get('capabilities', []),
                'qos_level': metadata.get('qos_level', 'normal'),
                'file_path': str(md_file),
                'version': metadata.get('version', '1.0.0'),
                'status': 'active'
            }
    
    yaml_data['agents'] = list(agent_map.values())
    yaml_data['last_updated'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    save_yaml(AGENTS_YAML, yaml_data)
    print(f"已同步 {len(agent_map)} 个智能体配置")

def sync_skills_md_to_yaml():
    """同步技能Markdown文件到YAML配置"""
    yaml_data = load_yaml(SKILLS_YAML)
    skills = yaml_data.get('skills', [])
    
    skill_map = {skill['skill_id']: skill for skill in skills}
    
    for skill_dir in SKILLS_MD_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        
        md_file = skill_dir / "SKILL.md"
        if not md_file.exists():
            continue
        
        content = md_file.read_text(encoding='utf-8')
        metadata = extract_metadata_from_md(content)
        
        skill_id = skill_dir.name
        
        if skill_id in skill_map:
            skill_map[skill_id]['description'] = metadata.get('description', skill_map[skill_id].get('description', ''))
            skill_map[skill_id]['version'] = metadata.get('version', skill_map[skill_id].get('version', '1.0.0'))
            skill_map[skill_id]['status'] = 'active'
        else:
            skill_map[skill_id] = {
                'skill_id': skill_id,
                'name': metadata.get('name', skill_id),
                'name_en': metadata.get('name_en', f"{skill_id} Skill"),
                'description': metadata.get('description', ''),
                'version': metadata.get('version', '1.0.0'),
                'author': 'system',
                'entry_point': str(skill_dir / "__init__.py"),
                'definition_file': str(md_file),
                'permissions': [],
                'dependencies': [],
                'status': 'active'
            }
    
    yaml_data['skills'] = list(skill_map.values())
    yaml_data['last_updated'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    save_yaml(SKILLS_YAML, yaml_data)
    print(f"已同步 {len(skill_map)} 个技能配置")

def sync_workflows_md_to_yaml():
    """同步工作流Markdown文件到YAML配置"""
    # 从workflow-templates.md提取工作流配置
    md_file = RULES_MD_DIR / "workflow-templates.md"
    if not md_file.exists():
        return
    
    content = md_file.read_text(encoding='utf-8')
    
    # 解析工作流模板
    templates = []
    template_pattern = re.compile(r'##\s*(\d+)\.\s*(\S+)\s*\n\n###\s*名称\s*\n(.+?)\n\n###\s*说明\s*\n(.+?)(?=\n##|$)', re.DOTALL)
    
    for match in template_pattern.finditer(content):
        template_id = match.group(2).lower().replace(' ', '_')
        name = match.group(3).strip()
        description = match.group(4).strip()
        
        templates.append({
            'template_id': template_id,
            'name': name,
            'name_en': f"{template_id.replace('_', ' ').title()} Workflow",
            'description': description,
            'qos_level': 'normal',
            'execution_mode': template_id,
            'parameters': {}
        })
    
    yaml_data = load_yaml(WORKFLOWS_YAML)
    yaml_data['templates'] = templates
    yaml_data['last_updated'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    save_yaml(WORKFLOWS_YAML, yaml_data)
    print(f"已同步 {len(templates)} 个工作流模板")

def sync_yaml_to_md():
    """从YAML配置生成Markdown文件"""
    # 生成智能体Markdown文件
    yaml_data = load_yaml(AGENTS_YAML)
    
    for agent in yaml_data.get('agents', []):
        md_content = f"""---
name_en: {agent.get('name_en', '')}
description: {agent.get('description', '')}
capabilities: {json.dumps(agent.get('capabilities', []))}
qos_level: {agent.get('qos_level', 'normal')}
version: {agent.get('version', '1.0.0')}
---

# {agent['name']} ({agent['name_en']})

## 描述

{agent.get('description', '')}

## 能力

{chr(10).join([f"- {cap}" for cap in agent.get('capabilities', [])])}

## 配置

- **QoS级别**: {agent.get('qos_level', 'normal')}
- **版本**: {agent.get('version', '1.0.0')}
- **状态**: {agent.get('status', 'active')}
"""
        md_path = AGENTS_MD_DIR / f"{agent['id']}_{agent['name']}_agent.md"
        md_path.write_text(md_content, encoding='utf-8')
    
    print("已从YAML生成Markdown文件")

def start_watcher():
    """启动文件监听"""
    event_handler = SyncEventHandler()
    observer = Observer()
    
    # 监听智能体目录
    if AGENTS_MD_DIR.exists():
        observer.schedule(event_handler, str(AGENTS_MD_DIR), recursive=True)
    
    # 监听技能目录
    if SKILLS_MD_DIR.exists():
        observer.schedule(event_handler, str(SKILLS_MD_DIR), recursive=True)
    
    # 监听规则目录
    if RULES_MD_DIR.exists():
        observer.schedule(event_handler, str(RULES_MD_DIR), recursive=True)
    
    observer.start()
    print("文件监听已启动，按 Ctrl+C 停止")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Markdown-YAML 同步工具')
    parser.add_argument('--sync', action='store_true', help='执行一次同步')
    parser.add_argument('--watch', action='store_true', help='启动文件监听')
    parser.add_argument('--yaml-to-md', action='store_true', help='从YAML生成Markdown')
    
    args = parser.parse_args()
    
    if args.sync:
        sync_agents_md_to_yaml()
        sync_skills_md_to_yaml()
        sync_workflows_md_to_yaml()
        print("同步完成")
    
    elif args.yaml_to_md:
        sync_yaml_to_md()
        print("YAML转Markdown完成")
    
    elif args.watch:
        start_watcher()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()