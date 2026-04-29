# -*- coding: utf-8 -*-
"""
Meta-Cognition 自我更新模块

实现从规则文件自动同步配置的功能
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional

from .config.config import CONFIG, MetaCognitionConfig, KnowledgeGraphConfig
from .hooks.utils import load_log, save_log, get_current_timestamp


RULES_FILE = Path(__file__).parent.parent / "新建文档1.txt"


def parse_rules_file(file_path: Path) -> Dict[str, Any]:
    """
    解析规则文件，提取配置信息
    
    Args:
        file_path: 规则文件路径
    
    Returns:
        提取的配置信息
    """
    if not file_path.exists():
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] 读取规则文件失败: {e}")
        return {}
    
    parsed = {}
    
    # 提取知识图谱配置
    kg_section = re.search(r'### 11\.1\.1 知识图谱调用约定.*?### 11\.2', content, re.DOTALL)
    if kg_section:
        kg_content = kg_section.group(0)
        # 提取核心概念
        core_concepts_match = re.search(r'核心博弈概念：(.*?)。', kg_content)
        if core_concepts_match:
            core_concepts = [c.strip() for c in core_concepts_match.group(1).split('、')]
            parsed['core_concepts'] = core_concepts
        
        # 提取概念优先级
        priority_match = re.search(r'按预设优先级 \*\*(.*?)\*\*', content)
        if priority_match:
            priority = [p.strip() for p in priority_match.group(1).split(' > ')]
            parsed['concept_priority'] = priority
    
    # 提取触发规则
    trigger_section = re.search(r'### 11\.2 基于知识图谱的语义触发机制.*?### 11\.3', content, re.DOTALL)
    if trigger_section:
        parsed['trigger_mechanism'] = 'knowledge_graph'
    
    return parsed


def update_config_from_rules() -> bool:
    """
    从规则文件更新配置
    
    Returns:
        是否更新成功
    """
    if not CONFIG.enable_self_update:
        print("[INFO] 自我更新已禁用")
        return False
    
    parsed = parse_rules_file(RULES_FILE)
    if not parsed:
        print("[WARNING] 规则文件解析失败，跳过更新")
        return False
    
    # 更新知识图谱配置
    if 'core_concepts' in parsed:
        CONFIG.knowledge_graph.core_concepts = parsed['core_concepts']
    
    if 'concept_priority' in parsed:
        CONFIG.knowledge_graph.concept_priority = parsed['concept_priority']
    
    print("[INFO] 配置已从规则文件更新")
    return True


def check_and_update() -> bool:
    """
    检查并更新配置
    
    Returns:
        是否更新成功
    """
    log_data = load_log()
    last_update = log_data.get('last_config_update', '')
    
    # 检查规则文件是否有更新
    if RULES_FILE.exists():
        file_mtime = RULES_FILE.stat().st_mtime
        if not last_update or file_mtime > float(last_update.get('timestamp', '0')):
            success = update_config_from_rules()
            if success:
                log_data['last_config_update'] = {
                    'timestamp': str(file_mtime),
                    'time': get_current_timestamp(),
                    'success': True
                }
                save_log(log_data)
                return True
    
    return False


def get_update_status() -> Dict[str, Any]:
    """
    获取更新状态
    
    Returns:
        更新状态信息
    """
    log_data = load_log()
    last_update = log_data.get('last_config_update', {})
    
    return {
        'enabled': CONFIG.enable_self_update,
        'rules_file_exists': RULES_FILE.exists(),
        'last_update': last_update,
        'rules_file_path': str(RULES_FILE)
    }


def force_update() -> Dict[str, Any]:
    """
    强制更新配置
    
    Returns:
        更新结果
    """
    success = update_config_from_rules()
    
    log_data = load_log()
    log_data['last_config_update'] = {
        'timestamp': str(RULES_FILE.stat().st_mtime) if RULES_FILE.exists() else '0',
        'time': get_current_timestamp(),
        'success': success,
        'forced': True
    }
    save_log(log_data)
    
    return {
        'success': success,
        'message': '配置已强制更新' if success else '更新失败',
        'rules_file': str(RULES_FILE)
    }


if __name__ == "__main__":
    print("=== 自我更新模块测试 ===")
    print(f"规则文件路径: {RULES_FILE}")
    print(f"规则文件存在: {RULES_FILE.exists()}")
    
    status = get_update_status()
    print(f"更新状态: {status}")
    
    result = check_and_update()
    print(f"检查并更新: {'成功' if result else '失败'}")
    
    force_result = force_update()
    print(f"强制更新: {force_result}")
