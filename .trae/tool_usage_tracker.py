"""
工具调用追踪系统 v1.0
追踪 MCP 和 Skills 的调用情况，生成每日报告
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading


@dataclass
class ToolCallRecord:
    tool_type: str
    tool_name: str
    action: str
    timestamp: str
    status: str
    duration_ms: float
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ToolUsageTracker:
    BASE_DIR = Path(__file__).parent
    LOGS_DIR = BASE_DIR / "logs"
    REPORTS_DIR = BASE_DIR / "reports"
    
    def __init__(self):
        self.LOGS_DIR.mkdir(exist_ok=True)
        self.REPORTS_DIR.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        self._current_session: List[ToolCallRecord] = []
        
    def _get_today_log_path(self) -> Path:
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.LOGS_DIR / f"tool_calls_{date_str}.json"
    
    def _get_report_path(self, date: Optional[str] = None) -> Path:
        date_str = date or datetime.now().strftime("%Y-%m-%d")
        return self.REPORTS_DIR / f"工具调用日报_{date_str}.md"
    
    def record_call(
        self,
        tool_type: str,
        tool_name: str,
        action: str,
        status: str,
        duration_ms: float,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        record = ToolCallRecord(
            tool_type=tool_type,
            tool_name=tool_name,
            action=action,
            timestamp=datetime.now().isoformat(),
            status=status,
            duration_ms=duration_ms,
            error=error,
            metadata=metadata
        )
        
        with self._lock:
            self._current_session.append(record)
            self._append_to_log(record)
        
        return record.timestamp
    
    def _append_to_log(self, record: ToolCallRecord):
        log_path = self._get_today_log_path()
        
        records = []
        if log_path.exists():
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except:
                records = []
        
        records.append(asdict(record))
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    def get_today_stats(self) -> Dict[str, Any]:
        log_path = self._get_today_log_path()
        
        if not log_path.exists():
            return {
                "total_calls": 0,
                "mcp_calls": 0,
                "skill_calls": 0,
                "success_rate": 0,
                "avg_duration_ms": 0,
                "tools": {}
            }
        
        with open(log_path, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        stats = {
            "total_calls": len(records),
            "mcp_calls": 0,
            "skill_calls": 0,
            "success_count": 0,
            "error_count": 0,
            "total_duration_ms": 0,
            "tools": defaultdict(lambda: {"count": 0, "success": 0, "error": 0, "total_duration": 0})
        }
        
        for r in records:
            if r["tool_type"] == "mcp":
                stats["mcp_calls"] += 1
            elif r["tool_type"] == "skill":
                stats["skill_calls"] += 1
            
            if r["status"] == "success":
                stats["success_count"] += 1
            else:
                stats["error_count"] += 1
            
            stats["total_duration_ms"] += r["duration_ms"]
            
            tool_key = f"{r['tool_type']}:{r['tool_name']}"
            stats["tools"][tool_key]["count"] += 1
            stats["tools"][tool_key]["total_duration"] += r["duration_ms"]
            if r["status"] == "success":
                stats["tools"][tool_key]["success"] += 1
            else:
                stats["tools"][tool_key]["error"] += 1
        
        stats["success_rate"] = (
            stats["success_count"] / stats["total_calls"] * 100 
            if stats["total_calls"] > 0 else 0
        )
        stats["avg_duration_ms"] = (
            stats["total_duration_ms"] / stats["total_calls"]
            if stats["total_calls"] > 0 else 0
        )
        
        return stats
    
    def generate_daily_report(self, date: Optional[str] = None) -> str:
        if date:
            log_path = self.LOGS_DIR / f"tool_calls_{date}.json"
        else:
            log_path = self._get_today_log_path()
        
        if not log_path.exists():
            return f"# 工具调用日报\n\n**日期**: {date or datetime.now().strftime('%Y-%m-%d')}\n\n⚠️ 当日无调用记录\n"
        
        with open(log_path, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        stats = self._calculate_stats(records)
        report = self._format_report(stats, records, date)
        
        report_path = self._get_report_path(date)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report
    
    def _calculate_stats(self, records: List[Dict]) -> Dict:
        stats = {
            "total_calls": len(records),
            "mcp_calls": 0,
            "skill_calls": 0,
            "success_count": 0,
            "error_count": 0,
            "total_duration_ms": 0,
            "tools": defaultdict(lambda: {
                "count": 0, "success": 0, "error": 0, 
                "total_duration": 0, "actions": defaultdict(int)
            }),
            "hourly": defaultdict(lambda: {"mcp": 0, "skill": 0})
        }
        
        for r in records:
            if r["tool_type"] == "mcp":
                stats["mcp_calls"] += 1
            elif r["tool_type"] == "skill":
                stats["skill_calls"] += 1
            
            if r["status"] == "success":
                stats["success_count"] += 1
            else:
                stats["error_count"] += 1
            
            stats["total_duration_ms"] += r["duration_ms"]
            
            tool_key = r["tool_name"]
            stats["tools"][tool_key]["count"] += 1
            stats["tools"][tool_key]["total_duration"] += r["duration_ms"]
            stats["tools"][tool_key]["type"] = r["tool_type"]
            if r["status"] == "success":
                stats["tools"][tool_key]["success"] += 1
            else:
                stats["tools"][tool_key]["error"] += 1
            stats["tools"][tool_key]["actions"][r["action"]] += 1
            
            hour = datetime.fromisoformat(r["timestamp"]).hour
            stats["hourly"][hour][r["tool_type"]] += 1
        
        stats["success_rate"] = (
            stats["success_count"] / stats["total_calls"] * 100 
            if stats["total_calls"] > 0 else 0
        )
        stats["avg_duration_ms"] = (
            stats["total_duration_ms"] / stats["total_calls"]
            if stats["total_calls"] > 0 else 0
        )
        
        return stats
    
    def _format_report(self, stats: Dict, records: List[Dict], date: Optional[str]) -> str:
        date_str = date or datetime.now().strftime("%Y-%m-%d")
        
        lines = [
            f"# 工具调用日报",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**报告日期**: {date_str}",
            "",
            "---",
            "",
            "## 📊 总体统计",
            "",
            "| 指标 | 数值 |",
            "|------|------|",
            f"| 总调用次数 | {stats['total_calls']} |",
            f"| MCP 调用次数 | {stats['mcp_calls']} |",
            f"| Skill 调用次数 | {stats['skill_calls']} |",
            f"| 成功率 | {stats['success_rate']:.1f}% |",
            f"| 平均耗时 | {stats['avg_duration_ms']:.2f}ms |",
            f"| 总耗时 | {stats['total_duration_ms']:.2f}ms |",
            "",
            "---",
            "",
            "## 🔧 工具详情",
            "",
        ]
        
        sorted_tools = sorted(
            stats["tools"].items(), 
            key=lambda x: x[1]["count"], 
            reverse=True
        )
        
        for tool_name, tool_stats in sorted_tools:
            tool_type = tool_stats.get("type", "unknown")
            success_rate = (
                tool_stats["success"] / tool_stats["count"] * 100 
                if tool_stats["count"] > 0 else 0
            )
            avg_duration = (
                tool_stats["total_duration"] / tool_stats["count"]
                if tool_stats["count"] > 0 else 0
            )
            
            type_icon = "🔌" if tool_type == "mcp" else "⚡"
            
            lines.extend([
                f"### {type_icon} {tool_name}",
                "",
                "| 指标 | 数值 |",
                "|------|------|",
                f"| 类型 | {tool_type.upper()} |",
                f"| 调用次数 | {tool_stats['count']} |",
                f"| 成功/失败 | {tool_stats['success']}/{tool_stats['error']} |",
                f"| 成功率 | {success_rate:.1f}% |",
                f"| 平均耗时 | {avg_duration:.2f}ms |",
                "",
                "**操作分布**:",
                "",
            ])
            
            for action, count in sorted(tool_stats["actions"].items(), key=lambda x: -x[1]):
                lines.append(f"- `{action}`: {count}次")
            
            lines.append("")
        
        lines.extend([
            "---",
            "",
            "## ⏰ 时段分布",
            "",
            "| 时段 | MCP调用 | Skill调用 | 总计 |",
            "|------|---------|-----------|------|",
        ])
        
        for hour in range(24):
            hourly = stats["hourly"].get(hour, {"mcp": 0, "skill": 0})
            total = hourly["mcp"] + hourly["skill"]
            if total > 0:
                lines.append(
                    f"| {hour:02d}:00-{hour:02d}:59 | {hourly['mcp']} | {hourly['skill']} | {total} |"
                )
        
        if stats["error_count"] > 0:
            lines.extend([
                "",
                "---",
                "",
                "## ❌ 错误记录",
                "",
            ])
            
            error_records = [r for r in records if r["status"] == "error"]
            for r in error_records[:10]:
                lines.append(f"- **{r['tool_name']}** ({r['timestamp']}): {r.get('error', '未知错误')}")
        
        lines.extend([
            "",
            "---",
            "",
            "*报告由 TRAE 工具调用追踪系统自动生成*",
        ])
        
        return "\n".join(lines)
    
    def list_available_reports(self) -> List[str]:
        reports = list(self.REPORTS_DIR.glob("工具调用日报_*.md"))
        return sorted([r.stem for r in reports], reverse=True)


_tracker_instance: Optional[ToolUsageTracker] = None

def get_tracker() -> ToolUsageTracker:
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ToolUsageTracker()
    return _tracker_instance


def track_mcp_call(tool_name: str, action: str, status: str, duration_ms: float, 
                   error: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
    return get_tracker().record_call("mcp", tool_name, action, status, duration_ms, error, metadata)


def track_skill_call(tool_name: str, action: str, status: str, duration_ms: float,
                     error: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
    return get_tracker().record_call("skill", tool_name, action, status, duration_ms, error, metadata)


if __name__ == "__main__":
    tracker = get_tracker()
    
    report = tracker.generate_daily_report()
    print(report)
    print(f"\n报告已保存到: {tracker.REPORTS_DIR}")
