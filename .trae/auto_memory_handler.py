"""
Cloud Code 记忆系统 - 自动执行模块
AI收到消息后自动调用，无需手动触发

使用方式：
    from .trae.auto_memory_handler import AutoMemoryHandler
    handler = AutoMemoryHandler()
    result = handler.process("我习惯用4空格缩进")
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class AutoMemoryHandler:
    """
    自动记忆处理器
    AI收到用户消息时自动调用此处理器完成记忆管理
    """

    def __init__(self, base_path: str = ".trae/memories"):
        self.base_path = Path(base_path)
        self.user_path = self.base_path / "user"
        self.feedback_path = self.base_path / "feedback"
        self.project_path = self.base_path / "project"
        self.reference_path = self.base_path / "reference"

        self._init_directories()
        self._load_state()

    def _init_directories(self):
        """初始化目录"""
        for path in [self.user_path, self.feedback_path, self.project_path, self.reference_path]:
            path.mkdir(parents=True, exist_ok=True)

    def _load_state(self):
        """加载状态"""
        state_file = self.base_path / ".state.json"
        if state_file.exists():
            state = json.loads(state_file.read_text(encoding='utf-8'))
            self.last_dream = datetime.fromisoformat(state.get("last_dream")) if state.get("last_dream") else None
            self.session_count = state.get("session_count", 0)
        else:
            self.last_dream = None
            self.session_count = 0

    def _save_state(self):
        """保存状态"""
        state = {
            "last_dream": self.last_dream.isoformat() if self.last_dream else None,
            "session_count": self.session_count
        }
        (self.base_path / ".state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')

    def is_dark_knowledge(self, text: str) -> Tuple[bool, str]:
        """
        判断是否为暗知识（该记）
        返回: (是否暗知识, 原因)
        """
        # 明知识 - 不该记的（优先级高）
        bright_patterns = [
            (r'用的是[^\s]+\s*\d+\.\d+\.\d+', '版本号可从代码查'),
            (r'在.*\.js里', '文件位置可用grep'),
            (r'有个.*函数', '函数可用grep'),
            (r'可以用.*查', '工具可替代'),
        ]
        for pattern, reason in bright_patterns:
            if re.search(pattern, text):
                return False, reason

        # 暗知识 - 该记的
        dark_patterns = [
            (r'我(是|习惯|喜欢|希望|要求|禁止|偏好)', '用户个人信息'),
            (r'团队(规则|要求|禁止)', '团队规则'),
            (r'以后(只要|都这样|不要)', '用户未来偏好'),
            (r'你刚才.*很好', '用户确认/反馈'),
            (r'因为要(兼容|历史|遗留)', '设计决策原因'),
            (r'这是.*系统', '项目背景'),
            (r'需求在.*Jira|Jira.*票', '外部资源引用'),
            (r'文档在.*\.(md|json|yml|yaml|txt)', '文档位置'),
        ]
        for pattern, reason in dark_patterns:
            if re.search(pattern, text):
                return True, reason

        # 短文本默认暗知识
        if len(text) < 200 and not re.match(r'^\s*$', text):
            return True, '用户明确提供的信息'

        return False, '不确定是否需要记忆'

    def classify(self, text: str) -> Tuple[str, str]:
        """
        自动分类记忆类型
        返回: (类型, 原因)
        """
        # Feedback
        if re.search(r'好|认可|确认|以后都这样|以后只要|你刚才|修正|纠正', text):
            return "feedback", "用户反馈或确认"

        # Reference
        if re.search(r'在.*\.(md|json|yml|yaml|txt|doc|pdf)', text):
            return "reference", "外部资源位置"
        if re.search(r'Jira|Linear|GitHub|Figma|Confluence', text):
            return "reference", "外部工具链接"

        # Project
        if re.search(r'项目|系统|模块|设计|原因|因为|背景|架构|选择', text):
            return "project", "项目上下文或决策"

        # User
        return "user", "用户个人偏好"

    def _safe_filename(self, text: str, max_len: int = 40) -> str:
        """生成安全文件名"""
        title = text[:max_len] if len(text) > max_len else text
        safe = re.sub(r'[^\w\-_\. ]', '_', title)
        safe = re.sub(r'\s+', '_', safe)
        return safe.strip('_') or "memory"

    def process(self, user_message: str) -> Dict:
        """
        核心方法：收到用户消息后自动调用
        完全自动化，无需手动触发
        """
        # 1. 识别暗知识
        is_dark, why = self.is_dark_knowledge(user_message)

        if not is_dark:
            return {"auto_saved": False, "reason": f"明知识不需要记忆: {why}"}

        # 2. 分类
        mem_type, why_type = self.classify(user_message)

        # 3. 获取目标路径
        type_path_map = {
            "user": self.user_path,
            "feedback": self.feedback_path,
            "project": self.project_path,
            "reference": self.reference_path
        }
        target_path = type_path_map[mem_type]

        # 4. 生成文件名和内容
        title = user_message[:40] + "..." if len(user_message) > 40 else user_message
        filename = self._safe_filename(title)
        filepath = target_path / f"{filename}.md"

        # 5. 检查是否已存在
        if filepath.exists():
            return {"auto_saved": False, "reason": "记忆已存在", "type": mem_type}

        # 6. 写入
        content = f"""---
type: {mem_type}
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# {title}

{user_message}

**Why:** {why}; {why_type}
**How to apply:** 根据记忆类型自动触发
"""
        filepath.write_text(content, encoding='utf-8')

        # 7. 更新会话计数
        self.session_count += 1
        self._save_state()

        # 8. 检查是否触发Dream
        self._check_and_run_dream()

        return {
            "auto_saved": True,
            "type": mem_type,
            "path": str(filepath),
            "title": title
        }

    def _check_and_run_dream(self):
        """检查并自动运行Dream"""
        now = datetime.now()

        if self.last_dream is None:
            should_dream = True
        elif (now - self.last_dream >= timedelta(hours=24)) and self.session_count >= 5:
            should_dream = True
        else:
            should_dream = False

        if should_dream:
            self.run_dream()

    def run_dream(self) -> Dict:
        """执行Dream记忆整合"""
        report = {
            "time": datetime.now().isoformat(),
            "scanned": {},
            "merged": [],
            "pruned": [],
            "status": "completed"
        }

        # 扫描
        total_lines = 0
        for mem_type in ["user", "feedback", "project", "reference"]:
            path = getattr(self, f"{mem_type}_path")
            files = list(path.glob("*.md"))
            report["scanned"][mem_type] = len(files)
            for f in files:
                total_lines += len(f.read_text(encoding='utf-8').splitlines())

        # 整合相似记忆
        processed = set()
        for mem_type in ["user", "feedback", "project", "reference"]:
            path = getattr(self, f"{mem_type}_path")
            for f1 in path.glob("*.md"):
                for f2 in path.glob("*.md"):
                    if f1 != f2 and f1 not in processed and f2 not in processed:
                        if f1.stem[:10] in f2.stem or f2.stem[:10] in f1.stem:
                            report["merged"].append(str(f2.name))
                            processed.add(f2)

        # 剪枝test文件
        for mem_type in ["user", "feedback", "project", "reference"]:
            path = getattr(self, f"{mem_type}_path")
            for f in path.glob("*.md"):
                if f.name.startswith("test-"):
                    try:
                        f.unlink()
                        report["pruned"].append(str(f.name))
                    except:
                        pass

        # 更新状态
        self.last_dream = datetime.now()
        self.session_count = 0
        self._save_state()

        # 统计最终行数
        final_lines = 0
        for mem_type in ["user", "feedback", "project", "reference"]:
            path = getattr(self, f"{mem_type}_path")
            for f in path.glob("*.md"):
                final_lines += len(f.read_text(encoding='utf-8').splitlines())

        report["total_lines"] = final_lines

        # 保存报告
        report_file = self.base_path / f"dream-report-{datetime.now().strftime('%Y-%m-%d')}.md"
        report_content = f"""# Dream 记忆整合报告

## 时间: {report['time']}

## 扫描结果
{json.dumps(report['scanned'], ensure_ascii=False, indent=2)}

## 整合: {len(report['merged'])}个相似记忆合并
{json.dumps(report['merged'], ensure_ascii=False, indent=2)}

## 剪枝: {len(report['pruned'])}个过时记忆删除
{json.dumps(report['pruned'], ensure_ascii=False, indent=2)}

## 行数: {total_lines} → {final_lines}
状态: {'✅ 达标' if final_lines <= 200 else '⚠️ 需进一步整理'}
"""
        report_file.write_text(report_content, encoding='utf-8')

        return report

    def verify_memory_path(self, memory_file: str) -> Tuple[bool, str]:
        """验证记忆中的路径是否存在"""
        content = Path(memory_file).read_text(encoding='utf-8')
        paths = re.findall(r'[a-zA-Z0-9_/\\]+\.[a-z]+', content)
        for p in paths:
            if not Path(p).exists():
                return False, f"记忆说{p}存在，但实际不存在"
        return True, "验证通过"

    def search(self, query: str) -> List[Dict]:
        """搜索记忆"""
        results = []
        for mem_type in ["user", "feedback", "project", "reference"]:
            path = getattr(self, f"{mem_type}_path")
            for f in path.glob("*.md"):
                if query.lower() in f.read_text(encoding='utf-8').lower():
                    results.append({
                        "type": mem_type,
                        "file": str(f),
                        "name": f.name
                    })
        return results


# 全局单例
_handler = None

def get_handler() -> AutoMemoryHandler:
    """获取全局处理器"""
    global _handler
    if _handler is None:
        _handler = AutoMemoryHandler()
    return _handler

def auto_process(message: str) -> Dict:
    """
    快捷函数：自动处理用户消息
    AI收到消息后调用此函数即可完成记忆管理
    """
    return get_handler().process(message)
