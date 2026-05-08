# -*- coding: utf-8 -*-
"""
L1-L2-L3 三层规则同步引擎
实现三层规则的双向同步机制，支持实时同步
"""

import os
import json
import yaml
import re
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

class SyncDirection(Enum):
    """同步方向"""
    L1_TO_L2 = "L1→L2"
    L2_TO_L3 = "L2→L3"
    L1_TO_L2_TO_L3 = "L1→L2→L3"
    L3_TO_L2 = "L3→L2"
    L2_TO_L1 = "L2→L1"
    L3_TO_L2_TO_L1 = "L3→L2→L1"
    BIDIRECTIONAL = "双向同步"

class ConflictStrategy(Enum):
    """冲突解决策略"""
    L1_PRIORITY = "L1优先"
    L2_PRIORITY = "L2优先"
    L3_PRIORITY = "L3优先"
    TIMESTAMP_PRIORITY = "时间戳优先"
    MANUAL_REVIEW = "人工审核"

class SyncStatus(Enum):
    """同步状态"""
    SYNCED = "已同步"
    PENDING = "待同步"
    CONFLICT = "冲突"
    ERROR = "错误"

class SyncLog:
    """同步日志"""
    def __init__(self):
        self.entries = []
        self.lock = threading.Lock()
    
    def add_entry(self, direction: SyncDirection, source: str, target: str, 
                  status: SyncStatus, message: str = ""):
        """添加日志条目"""
        with self.lock:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "direction": direction.value,
                "source": source,
                "target": target,
                "status": status.value,
                "message": message
            }
            self.entries.append(entry)
    
    def get_recent(self, limit: int = 10) -> List[Dict]:
        """获取最近的日志"""
        with self.lock:
            return self.entries[-limit:]
    
    def clear(self):
        """清空日志"""
        with self.lock:
            self.entries = []

class RuleFileHandler(FileSystemEventHandler):
    """文件系统事件处理器"""
    
    def __init__(self, sync_engine: 'SyncEngine', callback: Optional[Callable] = None):
        self.sync_engine = sync_engine
        self.callback = callback
        self.last_event_time = {}
        self.debounce_delay = 1.0  # 防抖延迟1秒
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        now = time.time()
        
        # 防抖处理
        if file_path in self.last_event_time:
            if now - self.last_event_time[file_path] < self.debounce_delay:
                return
        
        self.last_event_time[file_path] = now
        
        # 判断修改的是哪一层
        base_path = self.sync_engine.base_path
        l1_path = self.sync_engine.l1_path
        l2_path = self.sync_engine.l2_path
        l3_path = self.sync_engine.l3_path
        
        try:
            if file_path == l1_path:
                # L1修改，触发向下同步
                self._handle_l1_change()
            elif file_path == l2_path:
                # L2修改，触发双向同步
                self._handle_l2_change()
            elif l3_path in file_path.parents:
                # L3修改，触发向上同步
                self._handle_l3_change(file_path)
        except Exception as e:
            self.sync_engine.log.add_entry(
                SyncDirection.BIDIRECTIONAL,
                str(file_path),
                "unknown",
                SyncStatus.ERROR,
                f"实时同步异常: {str(e)}"
            )
    
    def on_created(self, event):
        """文件创建事件"""
        if not event.is_directory:
            self.on_modified(event)
    
    def on_deleted(self, event):
        """文件删除事件"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        self.sync_engine.log.add_entry(
            SyncDirection.BIDIRECTIONAL,
            str(file_path),
            "deleted",
            SyncStatus.PENDING,
            "文件已删除，需要重新同步"
        )
    
    def _handle_l1_change(self):
        """处理L1层变更"""
        if self.sync_engine.real_time_enabled:
            self.sync_engine.log.add_entry(
                SyncDirection.L1_TO_L2_TO_L3,
                "L1",
                "L3",
                SyncStatus.PENDING,
                "检测到L1变更，自动向下同步"
            )
            success = self.sync_engine.sync_downward()
            if self.callback:
                self.callback("L1_CHANGE", success)
    
    def _handle_l2_change(self):
        """处理L2层变更"""
        if self.sync_engine.real_time_enabled:
            self.sync_engine.log.add_entry(
                SyncDirection.BIDIRECTIONAL,
                "L2",
                "L1,L3",
                SyncStatus.PENDING,
                "检测到L2变更，自动双向同步"
            )
            results = self.sync_engine.sync_all()
            if self.callback:
                self.callback("L2_CHANGE", results)
    
    def _handle_l3_change(self, file_path: Path):
        """处理L3层变更"""
        if self.sync_engine.real_time_enabled:
            self.sync_engine.log.add_entry(
                SyncDirection.L3_TO_L2_TO_L1,
                str(file_path),
                "L1",
                SyncStatus.PENDING,
                f"检测到L3变更: {file_path.name}，自动向上同步"
            )
            success = self.sync_engine.sync_upward()
            if self.callback:
                self.callback("L3_CHANGE", success)

class SyncEngine:
    """三层同步引擎"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.l1_path = self.base_path / "agent.md"
        self.l2_path = self.base_path / ".trae" / "agent.md"
        self.l3_path = self.base_path / ".trae" / "rules"
        
        self.conflict_strategy = ConflictStrategy.L1_PRIORITY
        self.log = SyncLog()
        self.last_sync_time = None
        
        # 实时同步相关
        self.real_time_enabled = False
        self.observer = None
        self.handler = None
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self._file_mtimes = {}  # 记录文件修改时间
        
    def set_conflict_strategy(self, strategy: ConflictStrategy):
        """设置冲突解决策略"""
        self.conflict_strategy = strategy
    
    def _read_markdown_section(self, content: str, section_title: str) -> Optional[str]:
        """读取Markdown文件中的指定章节"""
        pattern = rf"##\s+{re.escape(section_title)}[\s\S]*?(?=##\s+|$)"
        match = re.search(pattern, content)
        return match.group(0) if match else None
    
    def _parse_section(self, content: str) -> Dict:
        """解析章节内容为结构化数据"""
        result = {}
        
        table_pattern = r"\|(.+)\|\n\|[-|]+\|\n((?:\|.+\|\n?)+)"
        tables = re.findall(table_pattern, content)
        for header_row, data_rows in tables:
            headers = [h.strip() for h in header_row.split("|") if h.strip()]
            rows = []
            for row in data_rows.strip().split("\n"):
                if row.strip():
                    cells = [c.strip() for c in row.split("|") if c.strip()]
                    if len(cells) == len(headers):
                        rows.append(dict(zip(headers, cells)))
            if headers:
                result[headers[0]] = rows
        
        yaml_pattern = r"```yaml\n([\s\S]*?)```"
        yaml_matches = re.findall(yaml_pattern, content)
        for yaml_str in yaml_matches:
            try:
                yaml_data = yaml.safe_load(yaml_str)
                if isinstance(yaml_data, dict):
                    result.update(yaml_data)
            except:
                pass
        
        json_pattern = r"```json\n([\s\S]*?)```"
        json_matches = re.findall(json_pattern, content)
        for json_str in json_matches:
            try:
                json_data = json.loads(json_str)
                if isinstance(json_data, dict):
                    result.update(json_data)
            except:
                pass
        
        return result
    
    def _write_markdown_section(self, content: str, section_title: str, 
                                new_content: str) -> str:
        """更新Markdown文件中的指定章节"""
        pattern = rf"(##\s+{re.escape(section_title)})([\s\S]*?)(?=##\s+|$)"
        replacement = f"\\1\n{new_content}\n\n"
        if re.search(pattern, content):
            return re.sub(pattern, replacement, content)
        else:
            return content + f"\n\n## {section_title}\n{new_content}"
    
    def get_l1_content(self) -> Optional[str]:
        """获取L1层内容"""
        if self.l1_path.exists():
            return self.l1_path.read_text(encoding="utf-8")
        return None
    
    def get_l2_content(self) -> Optional[str]:
        """获取L2层内容"""
        if self.l2_path.exists():
            return self.l2_path.read_text(encoding="utf-8")
        return None
    
    def get_l3_files(self) -> List[Path]:
        """获取L3层所有规则文件"""
        if self.l3_path.exists():
            return list(self.l3_path.rglob("*.md"))
        return []
    
    def _compare_sections(self, l1_content: str, l2_content: str, 
                         section_name: str) -> Tuple[bool, Dict, Dict]:
        """比较L1和L2的指定章节"""
        l1_section = self._read_markdown_section(l1_content, section_name)
        l2_section = self._read_markdown_section(l2_content, section_name)
        
        l1_data = self._parse_section(l1_section or "")
        l2_data = self._parse_section(l2_section or "")
        
        return l1_data == l2_data, l1_data, l2_data
    
    def check_sync_status(self) -> Dict[str, SyncStatus]:
        """检查各层级的同步状态"""
        status = {}
        
        l1_content = self.get_l1_content()
        l2_content = self.get_l2_content()
        
        if l1_content and l2_content:
            is_synced, _, _ = self._compare_sections(
                l1_content, l2_content, "三层双向同步规则"
            )
            status["L1-L2"] = SyncStatus.SYNCED if is_synced else SyncStatus.PENDING
        else:
            status["L1-L2"] = SyncStatus.ERROR
        
        l3_files = self.get_l3_files()
        required_dirs = ["core", "extension", "workflow", "agents"]
        l3_dirs = [d.name for d in self.l3_path.iterdir() if d.is_dir()]
        
        has_all_dirs = all(d in l3_dirs for d in required_dirs)
        has_core = any("智能体团队调度员" in f.name for f in l3_files)
        
        if has_all_dirs and has_core:
            status["L2-L3"] = SyncStatus.SYNCED
        else:
            status["L2-L3"] = SyncStatus.PENDING
        
        return status
    
    def sync_l1_to_l2(self) -> bool:
        """L1 → L2 同步"""
        l1_content = self.get_l1_content()
        l2_content = self.get_l2_content()
        
        if not l1_content or not l2_content:
            self.log.add_entry(
                SyncDirection.L1_TO_L2,
                str(self.l1_path),
                str(self.l2_path),
                SyncStatus.ERROR,
                "源文件或目标文件不存在"
            )
            return False
        
        l1_section = self._read_markdown_section(l1_content, "三层双向同步规则")
        if l1_section:
            l2_content = self._write_markdown_section(
                l2_content,
                "三层双向同步配置",
                l1_section.replace("三层双向同步规则", "").strip()
            )
            self.l2_path.write_text(l2_content, encoding="utf-8")
            
            self.log.add_entry(
                SyncDirection.L1_TO_L2,
                str(self.l1_path),
                str(self.l2_path),
                SyncStatus.SYNCED,
                "成功同步三层双向同步规则"
            )
            return True
        
        self.log.add_entry(
            SyncDirection.L1_TO_L2,
            str(self.l1_path),
            str(self.l2_path),
            SyncStatus.ERROR,
            "未找到三层双向同步规则章节"
        )
        return False
    
    def sync_l2_to_l3(self) -> bool:
        """L2 → L3 同步"""
        l2_content = self.get_l2_content()
        if not l2_content:
            self.log.add_entry(
                SyncDirection.L2_TO_L3,
                str(self.l2_path),
                str(self.l3_path),
                SyncStatus.ERROR,
                "L2配置文件不存在"
            )
            return False
        
        required_dirs = ["core", "extension", "workflow", "agents"]
        for dir_name in required_dirs:
            dir_path = self.l3_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
        
        core_file = self.l3_path / "core" / "智能体团队调度员_v2.8.md"
        if not core_file.exists():
            core_content = self._generate_core_file()
            core_file.write_text(core_content, encoding="utf-8")
        
        self._update_l3_index()
        
        self.log.add_entry(
            SyncDirection.L2_TO_L3,
            str(self.l2_path),
            str(self.l3_path),
            SyncStatus.SYNCED,
            "成功同步目录结构和索引"
        )
        return True
    
    def _generate_core_file(self) -> str:
        """生成核心框架文件内容"""
        return """# 智能体团队调度员 v2.8

## 文档说明

本文档为智能体团队调度员核心框架 v2.8，提供智能体协调、任务分发、博弈调度等核心能力。

---

## 第一章：智能体概述

### 1.1 基本信息

| 属性 | 值 |
|-----|-----|
| 中文名 | 智能体团队调度员 |
| 英文名 | Agent Team Dispatcher |
| ID | dispatcher_agent |
| 版本 | v2.8 |
| 所属层级 | L3-R001 |

---

## 第二章：核心能力

| 能力类别 | 具体能力 |
|---------|---------|
| 中央调度 | 消息路由、负载均衡、结果聚合 |
| 博弈调度 | 辩论模式、降维打击、深度设计 |
| 知识图谱 | 语义索引、意图推断 |

---

## 第三章：执行流程

用户输入 → 任务分析 → 智能体选择 → 并行执行 → 结果聚合 → 返回用户

---

*最后更新: {}*
""".format(datetime.now().strftime("%Y-%m-%d"))
    
    def _update_l3_index(self):
        """更新L3层INDEX.md"""
        index_path = self.l3_path / "INDEX.md"
        if index_path.exists():
            content = index_path.read_text(encoding="utf-8")
            timestamp = datetime.now().strftime("%Y-%m-%d")
            if "自动更新" not in content:
                content += f"\n\n## 📝 更新日志\n\n| {timestamp} | v2.8.4 | 自动更新 |"
            index_path.write_text(content, encoding="utf-8")
        else:
            index_content = """# 规则索引 INDEX

> 本索引文件用于快速定位 `.trae\\rules\\` 目录下的所有规则文件。

---

## 📁 目录结构

```
.trae\\rules\\
├── CLAUDE.md                    # 规则入口文件
├── INDEX.md                     # 本索引文件
├── core/                       # 核心框架
├── extension/                  # 扩展模块
├── workflow/                   # 工作流模板
└── agents/                     # 智能体定义
```

---

## 📝 更新日志

| 日期 | 版本 | 更新内容 |
|-----|------|---------|
| {} | v2.8.4 | 自动生成索引 |

---

*最后更新: {}*
""".format(datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d"))
            index_path.write_text(index_content, encoding="utf-8")
    
    def sync_l3_to_l2(self) -> bool:
        """L3 → L2 同步"""
        l2_content = self.get_l2_content()
        if not l2_content:
            self.log.add_entry(
                SyncDirection.L3_TO_L2,
                str(self.l3_path),
                str(self.l2_path),
                SyncStatus.ERROR,
                "L2配置文件不存在"
            )
            return False
        
        modules = []
        for f in self.get_l3_files():
            rel_path = f.relative_to(self.l3_path)
            modules.append({
                "path": str(rel_path),
                "name": f.stem,
                "type": rel_path.parent.name
            })
        
        if modules:
            module_section = f"""### 13.6 L3模块清单

| 路径 | 名称 | 类型 |
|------|------|------|
{chr(10).join([f"| `{m['path']}` | {m['name']} | {m['type']} |" for m in modules])}"""
            
            l2_content = self._write_markdown_section(
                l2_content,
                "三层双向同步配置",
                module_section
            )
            self.l2_path.write_text(l2_content, encoding="utf-8")
        
        self.log.add_entry(
            SyncDirection.L3_TO_L2,
            str(self.l3_path),
            str(self.l2_path),
            SyncStatus.SYNCED,
            f"成功同步 {len(modules)} 个L3模块"
        )
        return True
    
    def sync_l2_to_l1(self) -> bool:
        """L2 → L1 同步"""
        l1_content = self.get_l1_content()
        l2_content = self.get_l2_content()
        
        if not l1_content or not l2_content:
            self.log.add_entry(
                SyncDirection.L2_TO_L1,
                str(self.l2_path),
                str(self.l1_path),
                SyncStatus.ERROR,
                "源文件或目标文件不存在"
            )
            return False
        
        l2_section = self._read_markdown_section(l2_content, "三层双向同步配置")
        if l2_section:
            l1_content = self._write_markdown_section(
                l1_content,
                "三层双向同步规则",
                l2_section.replace("三层双向同步配置", "").strip()
            )
            self.l1_path.write_text(l1_content, encoding="utf-8")
        
        self.log.add_entry(
            SyncDirection.L2_TO_L1,
            str(self.l2_path),
            str(self.l1_path),
            SyncStatus.SYNCED,
            "成功同步到L1层"
        )
        return True
    
    def sync_downward(self) -> bool:
        """向下同步: L1 → L2 → L3"""
        success = True
        
        self.log.add_entry(
            SyncDirection.L1_TO_L2_TO_L3,
            "L1",
            "L3",
            SyncStatus.PENDING,
            "开始向下同步"
        )
        
        success &= self.sync_l1_to_l2()
        success &= self.sync_l2_to_l3()
        
        if success:
            self.last_sync_time = datetime.now()
            self.log.add_entry(
                SyncDirection.L1_TO_L2_TO_L3,
                "L1",
                "L3",
                SyncStatus.SYNCED,
                "向下同步完成"
            )
        
        return success
    
    def sync_upward(self) -> bool:
        """向上同步: L3 → L2 → L1"""
        success = True
        
        self.log.add_entry(
            SyncDirection.L3_TO_L2_TO_L1,
            "L3",
            "L1",
            SyncStatus.PENDING,
            "开始向上同步"
        )
        
        success &= self.sync_l3_to_l2()
        success &= self.sync_l2_to_l1()
        
        if success:
            self.last_sync_time = datetime.now()
            self.log.add_entry(
                SyncDirection.L3_TO_L2_TO_L1,
                "L3",
                "L1",
                SyncStatus.SYNCED,
                "向上同步完成"
            )
        
        return success
    
    def sync_all(self) -> Dict[str, bool]:
        """执行完整的双向同步"""
        results = {
            "downward": self.sync_downward(),
            "upward": self.sync_upward()
        }
        return results
    
    def get_sync_report(self) -> Dict:
        """获取同步状态报告"""
        status = self.check_sync_status()
        return {
            "status": {k: v.value for k, v in status.items()},
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "conflict_strategy": self.conflict_strategy.value,
            "real_time_enabled": self.real_time_enabled,
            "recent_logs": self.log.get_recent(5)
        }
    
    # ============ 实时同步功能 ============
    
    def _polling_monitor(self):
        """轮询监控线程"""
        while not self.stop_event.is_set():
            try:
                self._check_file_changes()
            except Exception as e:
                self.log.add_entry(
                    SyncDirection.BIDIRECTIONAL,
                    "polling",
                    "monitor",
                    SyncStatus.ERROR,
                    f"轮询异常: {str(e)}"
                )
            time.sleep(2)  # 每2秒检查一次
    
    def _check_file_changes(self):
        """检查文件变化"""
        changed_files = []
        
        # 检查L1
        if self.l1_path.exists():
            mtime = self.l1_path.stat().st_mtime
            if self._file_mtimes.get(str(self.l1_path)) != mtime:
                self._file_mtimes[str(self.l1_path)] = mtime
                changed_files.append(("L1", self.l1_path))
        
        # 检查L2
        if self.l2_path.exists():
            mtime = self.l2_path.stat().st_mtime
            if self._file_mtimes.get(str(self.l2_path)) != mtime:
                self._file_mtimes[str(self.l2_path)] = mtime
                changed_files.append(("L2", self.l2_path))
        
        # 检查L3目录
        for f in self.get_l3_files():
            mtime = f.stat().st_mtime
            if self._file_mtimes.get(str(f)) != mtime:
                self._file_mtimes[str(f)] = mtime
                changed_files.append(("L3", f))
        
        # 处理变化
        for layer, file_path in changed_files:
            if layer == "L1":
                self.log.add_entry(
                    SyncDirection.L1_TO_L2_TO_L3,
                    "L1",
                    "L3",
                    SyncStatus.PENDING,
                    f"检测到L1变更: {file_path.name}"
                )
                self.sync_downward()
            elif layer == "L2":
                self.log.add_entry(
                    SyncDirection.BIDIRECTIONAL,
                    "L2",
                    "L1,L3",
                    SyncStatus.PENDING,
                    f"检测到L2变更: {file_path.name}"
                )
                self.sync_all()
            elif layer == "L3":
                self.log.add_entry(
                    SyncDirection.L3_TO_L2_TO_L1,
                    str(file_path),
                    "L1",
                    SyncStatus.PENDING,
                    f"检测到L3变更: {file_path.name}"
                )
                self.sync_upward()
    
    def start_real_time_sync(self, callback: Optional[Callable] = None) -> bool:
        """启动实时同步"""
        if self.real_time_enabled:
            return True
        
        # 初始化文件时间戳
        self._file_mtimes = {}
        if self.l1_path.exists():
            self._file_mtimes[str(self.l1_path)] = self.l1_path.stat().st_mtime
        if self.l2_path.exists():
            self._file_mtimes[str(self.l2_path)] = self.l2_path.stat().st_mtime
        for f in self.get_l3_files():
            self._file_mtimes[str(f)] = f.stat().st_mtime
        
        if WATCHDOG_AVAILABLE:
            # 使用watchdog进行高效监控
            self.handler = RuleFileHandler(self, callback)
            self.observer = Observer()
            
            # 监控L1文件
            if self.l1_path.exists():
                self.observer.schedule(self.handler, str(self.l1_path.parent), recursive=False)
            
            # 监控L2文件
            if self.l2_path.exists():
                self.observer.schedule(self.handler, str(self.l2_path.parent), recursive=False)
            
            # 监控L3目录
            if self.l3_path.exists():
                self.observer.schedule(self.handler, str(self.l3_path), recursive=True)
            
            self.observer.start()
            self.real_time_enabled = True
            self.log.add_entry(
                SyncDirection.BIDIRECTIONAL,
                "system",
                "real_time",
                SyncStatus.SYNCED,
                "实时同步已启动 (watchdog模式)"
            )
        else:
            # 使用轮询模式
            self.stop_event.clear()
            self.monitor_thread = threading.Thread(
                target=self._polling_monitor,
                daemon=True
            )
            self.monitor_thread.start()
            self.real_time_enabled = True
            self.log.add_entry(
                SyncDirection.BIDIRECTIONAL,
                "system",
                "real_time",
                SyncStatus.SYNCED,
                "实时同步已启动 (polling模式)"
            )
        
        return True
    
    def stop_real_time_sync(self):
        """停止实时同步"""
        if not self.real_time_enabled:
            return
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.handler = None
        elif self.monitor_thread:
            self.stop_event.set()
            self.monitor_thread.join()
            self.monitor_thread = None
        
        self.real_time_enabled = False
        self.log.add_entry(
            SyncDirection.BIDIRECTIONAL,
            "system",
            "real_time",
            SyncStatus.SYNCED,
            "实时同步已停止"
        )

# 全局同步引擎实例
_sync_engine = None

def get_sync_engine(base_path: str = ".") -> SyncEngine:
    """获取同步引擎实例"""
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = SyncEngine(base_path)
    return _sync_engine

# 命令行接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="L1-L2-L3 三层同步引擎")
    parser.add_argument("--check", action="store_true", help="检查同步状态")
    parser.add_argument("--sync-down", action="store_true", help="向下同步 L1→L2→L3")
    parser.add_argument("--sync-up", action="store_true", help="向上同步 L3→L2→L1")
    parser.add_argument("--sync-all", action="store_true", help="双向同步")
    parser.add_argument("--report", action="store_true", help="生成同步报告")
    parser.add_argument("--realtime-start", action="store_true", help="启动实时同步")
    parser.add_argument("--realtime-stop", action="store_true", help="停止实时同步")
    parser.add_argument("--path", default=".", help="项目路径")
    
    args = parser.parse_args()
    
    engine = SyncEngine(args.path)
    
    if args.check:
        status = engine.check_sync_status()
        print("同步状态检查:")
        for layer, st in status.items():
            print(f"  {layer}: {st.value}")
    
    elif args.sync_down:
        print("开始向下同步 (L1→L2→L3)...")
        success = engine.sync_downward()
        print("向下同步完成" if success else "向下同步失败")
    
    elif args.sync_up:
        print("开始向上同步 (L3→L2→L1)...")
        success = engine.sync_upward()
        print("向上同步完成" if success else "向上同步失败")
    
    elif args.sync_all:
        print("开始双向同步...")
        results = engine.sync_all()
        print(f"向下同步: {'成功' if results['downward'] else '失败'}")
        print(f"向上同步: {'成功' if results['upward'] else '失败'}")
    
    elif args.report:
        report = engine.get_sync_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    elif args.realtime_start:
        print("启动实时同步...")
        success = engine.start_real_time_sync()
        print("实时同步已启动" if success else "启动失败")
        print("按 Ctrl+C 停止...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            engine.stop_real_time_sync()
            print("\n实时同步已停止")
    
    elif args.realtime_stop:
        print("停止实时同步...")
        engine.stop_real_time_sync()
        print("实时同步已停止")
    
    else:
        parser.print_help()
