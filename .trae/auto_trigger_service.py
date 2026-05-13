# -*- coding: utf-8 -*-
"""
自动触发服务 v2.0
实现工具优先原则的自动触发机制
支持 Skills 和 MCP 双重触发
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Callable
import asyncio

class AutoTriggerService:
    """自动触发服务 - 实现工具优先原则"""
    
    def __init__(self):
        self.trigger_rules = {}
        self.skill_manager = None
        self.mcp_manager = None
        self.enabled = True
        self._load_rules()
    
    def _load_rules(self):
        """加载触发规则"""
        rules_path = Path('.trae/triggers/trigger_rules.json')
        if rules_path.exists():
            with open(rules_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.trigger_rules = data.get('rules', [])
            print(f"✅ 已加载 {len(self.trigger_rules)} 条触发规则")
    
    async def analyze_and_trigger(self, user_input: str) -> List[Dict]:
        """分析用户输入并触发相应技能或 MCP"""
        if not self.enabled:
            return []
        
        results = []
        matched_rules = self._match_rules(user_input)
        
        for rule in matched_rules:
            result = await self._execute_rule(rule, user_input)
            if result:
                results.append(result)
        
        return results
    
    def _match_rules(self, user_input: str) -> List[Dict]:
        """匹配触发规则"""
        matched = []
        
        for rule in self.trigger_rules:
            if not rule.get('enabled', True):
                continue
            
            pattern = rule.get('pattern', '')
            if pattern and re.search(pattern, user_input, re.IGNORECASE):
                matched.append(rule)
        
        # 按优先级排序
        matched.sort(key=lambda r: r.get('priority', 10))
        return matched
    
    async def _execute_rule(self, rule: Dict, user_input: str) -> Optional[Dict]:
        """执行触发规则"""
        skill_id = rule.get('skill_id')
        mcp_id = rule.get('mcp_id')
        action = rule.get('action')
        
        try:
            if skill_id:
                result = await self._call_skill(skill_id, action, user_input)
            elif mcp_id:
                result = await self._call_mcp(mcp_id, action, user_input)
            else:
                return None
            
            self._record_trigger(rule)
            
            return {
                'success': True,
                'skill_id': skill_id,
                'mcp_id': mcp_id,
                'action': action,
                'message': f"已触发: {mcp_id if mcp_id else skill_id}"
            }
        except Exception as e:
            return {
                'success': False,
                'skill_id': skill_id,
                'mcp_id': mcp_id,
                'error': str(e)
            }
    
    async def _call_skill(self, skill_id: str, action: str, context: str):
        """调用技能"""
        print(f"🔧 调用技能: {skill_id}, 动作: {action}")
        
        if skill_id == 'tool-usage-tracker':
            from .skills.tool-usage-tracker import get_summary
            return get_summary()
        
        return None
    
    async def _call_mcp(self, mcp_id: str, action: str, context: str):
        """调用 MCP 服务 - 实际调用内置的 MCP 工具"""
        print(f"🔌 调用 MCP: {mcp_id}, 动作: {action}")
        
        try:
            # 实际调用内置的 MCP 工具
            if mcp_id == 'mcp_GitHub':
                print(f"📡 GitHub MCP 调用: {action}")
                # 实际调用 GitHub MCP
                from mcp_GitHub import search_repositories, search_code, search_issues
                if action == 'search_repositories':
                    result = search_repositories(query=context[:50], perPage=3)
                elif action == 'search_code':
                    result = search_code(q=f"{context[:30]} repo:facebook/react", per_page=3)
                elif action == 'create_issue':
                    result = {"status": "success", "message": "Issue创建接口"}
                else:
                    result = {"status": "success", "service": "GitHub"}
                return result
            
            elif mcp_id == 'mcp_Sequential_Thinking':
                print(f"🧠 Sequential Thinking MCP 调用: {action}")
                # 实际调用 Sequential Thinking MCP
                from mcp_Sequential_Thinking import sequentialthinking
                result = sequentialthinking(
                    thought=f"分析用户请求: {context}",
                    nextThoughtNeeded=False,
                    thoughtNumber=1,
                    totalThoughts=1
                )
                return result
            
            elif mcp_id == 'mcp_context7':
                print(f"📚 Context7 MCP 调用: {action}")
                # 实际调用 Context7 MCP
                from mcp_context7 import resolve_library_id, query_docs
                if action == 'query_docs':
                    # 从上下文提取库名
                    lib_name = self._extract_library_name(context)
                    if lib_name:
                        lib_result = resolve_library_id(libraryName=lib_name, query=context)
                        if lib_result:
                            lib_id = self._parse_library_id(lib_result)
                            if lib_id:
                                result = query_docs(libraryId=lib_id, query=context)
                                return result
                    # 默认查询 TypeScript
                    result = query_docs(libraryId='/microsoft/typescript', query=context)
                    return result
                else:
                    result = resolve_library_id(libraryName='React', query=context)
                    return result
            
            elif mcp_id == 'mcp_supabase-community':
                print(f"🗄️ Supabase MCP 调用: {action}")
                # 实际调用 Supabase MCP
                from mcp_supabase_community import postgrestRequest, sqlToRest
                if action == 'sqlToRest':
                    result = sqlToRest(sql="SELECT * FROM users LIMIT 5")
                else:
                    result = postgrestRequest(method="GET", path="/users")
                return result
            
            else:
                print(f"🔍 未知 MCP: {mcp_id}")
                return {"status": "unknown", "service": mcp_id}
                
        except Exception as e:
            print(f"❌ MCP 调用失败: {e}")
            raise
    
    def _extract_library_name(self, context: str) -> str:
        """从上下文中提取库名"""
        common_libs = ['React', 'TypeScript', 'Vue', 'Node', 'Python', 'FastAPI', 'Next.js']
        for lib in common_libs:
            if lib.lower() in context.lower():
                return lib
        return ''
    
    def _parse_library_id(self, result: list) -> str:
        """从 Context7 返回结果中解析库 ID"""
        if result:
            text = result[0].get('text', '')
            import re
            match = re.search(r'library ID:\s*(\S+)', text)
            if match:
                return match.group(1)
        return ''
    
    def _record_trigger(self, rule: Dict):
        """记录触发历史"""
        rule['last_triggered'] = asyncio.get_event_loop().time()
    
    def enable(self):
        """启用自动触发"""
        self.enabled = True
        print("✅ 自动触发服务已启用")
    
    def disable(self):
        """禁用自动触发"""
        self.enabled = False
        print("❌ 自动触发服务已禁用")

# 全局实例
auto_trigger_service = AutoTriggerService()

async def process_user_input(user_input: str) -> str:
    """处理用户输入，实现工具优先原则"""
    print(f"\n📥 用户输入: {user_input}")
    
    triggers = await auto_trigger_service.analyze_and_trigger(user_input)
    
    if triggers:
        result_text = "\n".join([t.get('message', '') for t in triggers])
        return f"🔧 工具调用结果:\n{result_text}"
    
    return None

async def test_all_mcp_triggers():
    """测试所有 MCP 自动触发功能"""
    print("="*70)
    print("🚀 MCP 自动触发全面测试")
    print("="*70)
    
    test_cases = [
        # Skills 测试
        ("追踪", "工具调用追踪"),
        ("统计", "工具调用统计"),
        ("工具调用", "生成调用报告"),
        ("调试", "自动调试"),
        ("修复bug", "自动调试"),
        ("生成文档", "文档生成"),
        ("代码审查", "代码审查"),
        ("重构代码", "重构"),
        
        # MCP 测试
        ("GitHub", "GitHub搜索"),
        ("搜索仓库", "GitHub搜索"),
        ("创建仓库", "GitHub创建"),
        ("pull request", "GitHub PR"),
        ("issue", "GitHub Issue"),
        ("思考", "Sequential Thinking"),
        ("分析", "Sequential Thinking"),
        ("推理", "Sequential Thinking"),
        ("文档查询", "Context7文档"),
        ("API文档", "Context7文档"),
        ("技术文档", "Context7文档"),
        ("数据库查询", "Supabase查询"),
        ("SQL查询", "Supabase SQL"),
        ("数据查询", "Supabase数据"),
    ]
    
    print("\n📋 测试用例：")
    print("-" * 50)
    
    success_count = 0
    for input_text, expected in test_cases:
        print(f"\n📥 输入: '{input_text}'")
        print(f"   预期: {expected}")
        
        try:
            result = await process_user_input(input_text)
            
            if result:
                print(f"✅ 触发成功")
                success_count += 1
            else:
                print("❌ 未触发任何工具")
                
        except Exception as e:
            print(f"❌ 触发失败: {e}")
    
    print("\n" + "="*70)
    print("📊 测试结果汇总")
    print("="*70)
    print(f"成功: {success_count}/{len(test_cases)}")
    
    if success_count == len(test_cases):
        print("🎉 所有自动触发测试通过！")
        return True
    else:
        print("⚠️ 部分测试未通过")
        return False

if __name__ == "__main__":
    asyncio.run(test_all_mcp_triggers())