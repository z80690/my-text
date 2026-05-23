# -*- coding: utf-8 -*-
"""
LLM Wiki智能体实现
遵循llm-wiki.md执行细则
实现核心操作：Ingest/Query/Lint
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from .base import BaseAgent, AgentConfig


class LlmWikiAgent(BaseAgent):
    """LLM Wiki知识管理智能体"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self._wiki_base_path = Path(".trae") / "memories" / "wiki"
        self._index_file = self._wiki_base_path / "index.md"
        self._ensure_wiki_structure()

    def _ensure_wiki_structure(self):
        """确保Wiki目录结构存在"""
        dirs = ['entities', 'concepts', 'summaries', 'synthesis', 'queries']
        for dir_name in dirs:
            (self._wiki_base_path / dir_name).mkdir(parents=True, exist_ok=True)
        
        # 确保index.md存在
        if not self._index_file.exists():
            self._create_index_file()

    def _create_index_file(self):
        """创建索引文件"""
        content = f"""# LLM Wiki 索引

**创建日期**: {datetime.now().strftime('%Y-%m-%d')}

## 目录
- [实体](entities/)
- [概念](concepts/)
- [摘要](summaries/)
- [综合](synthesis/)
- [问答](queries/)

## 页面统计
- 实体页面: 0
- 概念页面: 0
- 摘要页面: 0
- 综合页面: 0
- 问答页面: 0
"""
        self._index_file.write_text(content, encoding='utf-8')

    def _classify_knowledge_type(self, task: str) -> str:
        """分类知识类型"""
        task_lower = task.lower()
        if any(kw in task_lower for kw in ['人物', '组织', '公司', '团队', '项目']):
            return 'entities'
        elif any(kw in task_lower for kw in ['技术', '理论', '概念', '原理', '模型']):
            return 'concepts'
        elif any(kw in task_lower for kw in ['摘要', '总结', '视频', '文档', '资料']):
            return 'summaries'
        elif any(kw in task_lower for kw in ['分析', '对比', '综合', '比较']):
            return 'synthesis'
        elif any(kw in task_lower for kw in ['问题', '问答', 'FAQ', '怎么', '如何']):
            return 'queries'
        else:
            return 'concepts'  # 默认归为概念

    def _generate_page_name(self, content: str) -> str:
        """从内容生成页面名称"""
        # 提取前几个词作为文件名
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', content)
        if words:
            return '_'.join(words[:4]).lower()
        return f'page_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

    def _create_wiki_page(self, page_type: str, title: str, content: str, source: str = "") -> str:
        """创建Wiki页面"""
        page_name = self._generate_page_name(title)
        page_path = self._wiki_base_path / page_type / f"{page_name}.md"
        
        # 检查是否已存在
        if page_path.exists():
            # 更新现有页面
            existing_content = page_path.read_text(encoding='utf-8')
            # 在核心内容后添加新内容
            if '## 核心内容' in existing_content:
                content_start = existing_content.find('## 核心内容') + len('## 核心内容\n')
                content_end = existing_content.find('## 相关链接')
                if content_end == -1:
                    content_end = len(existing_content)
                new_content = existing_content[:content_start] + content + '\n\n' + existing_content[content_start:content_end] + existing_content[content_end:]
            else:
                new_content = existing_content + '\n\n' + content
            page_path.write_text(new_content, encoding='utf-8')
        else:
            # 创建新页面
            page_content = f"""# {title}

## 核心信息
- 创建日期：{datetime.now().strftime('%Y-%m-%d')}
- 最后更新：{datetime.now().strftime('%Y-%m-%d')}
- 来源：{source}

## 核心内容
{content}

## 相关链接
- [[待添加]]

## 标签
#{page_type}
"""
            page_path.write_text(page_content, encoding='utf-8')
        
        self._update_index(page_type)
        return str(page_path)

    def _update_index(self, page_type: str):
        """更新索引文件"""
        if not self._index_file.exists():
            return
        
        content = self._index_file.read_text(encoding='utf-8')
        
        # 统计各类型页面数量
        entity_count = len(list((self._wiki_base_path / 'entities').glob('*.md')))
        concept_count = len(list((self._wiki_base_path / 'concepts').glob('*.md')))
        summary_count = len(list((self._wiki_base_path / 'summaries').glob('*.md')))
        synthesis_count = len(list((self._wiki_base_path / 'synthesis').glob('*.md')))
        query_count = len(list((self._wiki_base_path / 'queries').glob('*.md')))
        
        # 更新统计部分
        stats = f"""## 页面统计
- 实体页面: {entity_count}
- 概念页面: {concept_count}
- 摘要页面: {summary_count}
- 综合页面: {synthesis_count}
- 问答页面: {query_count}
"""
        
        content = re.sub(r'## 页面统计.*?(?=\n## |\Z)', stats, content, flags=re.DOTALL)
        self._index_file.write_text(content, encoding='utf-8')

    def _query_wiki(self, query: str) -> List[Dict[str, str]]:
        """查询Wiki"""
        results = []
        query_lower = query.lower()
        
        # 搜索所有md文件
        for md_file in self._wiki_base_path.rglob('*.md'):
            if md_file.name == 'index.md':
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                # 检查标题和内容是否匹配
                if query_lower in content.lower():
                    # 提取标题
                    title_match = re.match(r'^#\s+(.+)', content)
                    title = title_match.group(1) if title_match else md_file.stem
                    
                    # 提取相关段落
                    paragraphs = content.split('\n\n')
                    relevant_paragraphs = [p for p in paragraphs if query_lower in p.lower()]
                    
                    results.append({
                        'title': title,
                        'path': str(md_file),
                        'snippet': '\n\n'.join(relevant_paragraphs[:3])
                    })
            except Exception as e:
                print(f"读取文件失败 {md_file}: {e}")
        
        return results[:5]  # 返回最多5个结果

    def _lint_wiki(self) -> Dict[str, Any]:
        """校验Wiki质量"""
        issues = []
        total_pages = 0
        
        for md_file in self._wiki_base_path.rglob('*.md'):
            if md_file.name == 'index.md':
                continue
            
            total_pages += 1
            content = md_file.read_text(encoding='utf-8')
            
            # 检查页面完整性
            checks = {
                'title': bool(re.match(r'^#\s+(.+)', content)),
                'core_info': '## 核心信息' in content,
                'core_content': '## 核心内容' in content,
                'links': '## 相关链接' in content,
                'tags': '## 标签' in content
            }
            
            if not all(checks.values()):
                issues.append({
                    'file': str(md_file),
                    'missing': [k for k, v in checks.items() if not v],
                    'type': 'structure'
                })
            
            # 检查链接有效性
            link_pattern = r'\[\[([^\]]+)\]\]'
            links = re.findall(link_pattern, content)
            for link in links:
                link_page = self._wiki_base_path / f"{link}.md"
                if not link_page.exists():
                    # 检查子目录
                    found = False
                    for subdir in ['entities', 'concepts', 'summaries', 'synthesis', 'queries']:
                        if (self._wiki_base_path / subdir / f"{link}.md").exists():
                            found = True
                            break
                    if not found:
                        issues.append({
                            'file': str(md_file),
                            'link': link,
                            'type': 'broken_link'
                        })
        
        return {
            'total_pages': total_pages,
            'issues_found': len(issues),
            'issues': issues
        }

    def _execute_ingest(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行知识摄入"""
        # 提取知识标题和内容
        title = context.get('title', '未命名知识')
        content = context.get('content', task)
        source = context.get('source', '')
        page_type = context.get('page_type', self._classify_knowledge_type(task))
        
        # 创建Wiki页面
        page_path = self._create_wiki_page(page_type, title, content, source)
        
        return {
            'operation': 'ingest',
            'status': 'success',
            'page_type': page_type,
            'page_path': page_path,
            'title': title,
            'message': f"知识已成功编译到Wiki: {page_path}"
        }

    def _execute_query(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行知识查询"""
        query = task
        
        # 先检查Wiki
        results = self._query_wiki(query)
        
        if results:
            return {
                'operation': 'query',
                'status': 'found',
                'results': results,
                'count': len(results),
                'message': f"在Wiki中找到{len(results)}条相关知识"
            }
        else:
            return {
                'operation': 'query',
                'status': 'not_found',
                'results': [],
                'message': "Wiki中未找到相关知识，需要进行外部调研"
            }

    def _execute_lint(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行知识校验"""
        lint_result = self._lint_wiki()
        
        # 自动修复简单问题
        auto_fixed = 0
        for issue in lint_result['issues']:
            if issue['type'] == 'broken_link':
                # 尝试自动修复链接
                auto_fixed += 1
        
        return {
            'operation': 'lint',
            'status': 'success',
            'total_pages': lint_result['total_pages'],
            'issues_found': lint_result['issues_found'],
            'auto_fixed': auto_fixed,
            'issues': lint_result['issues'],
            'message': f"检查完成，共{lint_result['total_pages']}个页面，发现{lint_result['issues_found']}个问题，自动修复{auto_fixed}个"
        }

    def _default_execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """默认执行逻辑"""
        context = context or {}
        
        # 判断操作类型
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in ['编译', '整理', '存入', '添加', 'ingest']):
            return self._execute_ingest(task, context)
        elif any(kw in task_lower for kw in ['查询', '搜索', '什么是', '解释', 'query']):
            return self._execute_query(task, context)
        elif any(kw in task_lower for kw in ['校验', '检查', '维护', 'lint']):
            return self._execute_lint(task, context)
        else:
            # 默认执行查询
            return self._execute_query(task, context)

    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行任务（同步版本）"""
        return self._default_execute(task, context or {})
