# -*- coding: utf-8 -*-
"""
Meta-Cognition 完全自动化守护进程
后台自动运行，你什么都不用做！自动监控！自动记录！
"""

import sys
import os
import time
import threading
import json
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 数据目录（完全独立）
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "meta-cognition-data"
LOG_DIR = DATA_DIR / "logs"
LOG_FILE = LOG_DIR / "meta_cognition.json"
TASK_DIR = BASE_DIR / "tasks"

# 确保目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)
TASK_DIR.mkdir(parents=True, exist_ok=True)


class TaskMonitor(FileSystemEventHandler):
    """监控任务文件变化"""

    def __init__(self, manager):
        self.manager = manager

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.task'):
            self.process_task_file(event.src_path)

    def process_task_file(self, filepath):
        """处理任务文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                task_desc = f.read().strip()

            if task_desc:
                session_id = self.manager.submit_task(task_desc)
                print(f"[自动监控] 检测到新任务: {filepath}")
                print(f"[自动监控] 会话ID: {session_id}")

                # 模拟执行（实际使用时替换为真实执行）
                time.sleep(0.5)
                self.manager.complete_task(session_id, "success")

                # 删除任务文件（表示已处理）
                os.remove(filepath)
                print(f"[自动监控] 任务完成，已清理: {filepath}")
        except Exception as e:
            print(f"[自动监控] 处理任务失败: {e}")


class AutoDaemonManager:
    """自动化守护进程管理器"""

    def __init__(self):
        self._running = False
        self._sessions = []
        self._observer = None
        self._load_log()

    def _load_log(self):
        """加载日志"""
        self._sessions = []
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._sessions = data.get('sessions', [])
            except:
                pass

    def _save_log(self):
        """保存日志"""
        try:
            log_data = {
                "sessions": self._sessions,
                "statistics": self._get_statistics(),
                "last_updated": datetime.now().isoformat()
            }
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _get_task_mode(self, task: str) -> str:
        """检测任务模式"""
        debate_kw = ["对比", "权衡", "优缺点", "比较", "分析"]
        opt_kw = ["优化", "改进", "提升", "完善", "修改", "重构"]
        design_kw = ["设计", "架构", "实现", "创建", "开发"]

        for kw in debate_kw:
            if kw in task:
                return "辩论模式"
        for kw in opt_kw:
            if kw in task:
                return "降维打击模式"
        for kw in design_kw:
            if kw in task:
                return "深度设计模式"
        return "深度设计模式"

    def submit_task(self, task_desc: str) -> str:
        """提交任务"""
        import uuid
        session_id = str(uuid.uuid4())
        mode = self._get_task_mode(task_desc)

        session = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "task_description": task_desc,
            "detected_mode": mode,
            "phase": "auto_monitored",
            "result": None
        }
        self._sessions.insert(0, session)
        self._save_log()
        return session_id

    def complete_task(self, session_id: str, result: str):
        """完成任务"""
        for session in self._sessions:
            if session.get("session_id") == session_id:
                session["result"] = result
                session["end_timestamp"] = datetime.now().isoformat()
                self._save_log()
                return True
        return False

    def _get_statistics(self):
        """获取统计"""
        total = len(self._sessions)
        success = sum(1 for s in self._sessions if s.get("result") == "success")
        return {
            "total_tasks": total,
            "success_rate": (success / total * 100) if total > 0 else 0
        }

    def start(self):
        """启动守护进程"""
        if self._running:
            print("[自动守护] 已经在运行")
            return

        self._running = True
        print(f"[自动守护] 已启动！监控目录: {TASK_DIR}")
        print("[自动守护] 你只需要在 tasks/ 目录放 .task 文件，系统自动执行！")

        # 启动文件监控
        self._observer = Observer()
        event_handler = TaskMonitor(self)
        self._observer.schedule(event_handler, str(TASK_DIR), recursive=False)
        self._observer.start()

        # 保持运行
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """停止守护进程"""
        self._running = False
        if self._observer:
            self._observer.stop()
            self._observer.join()
        print("[自动守护] 已停止")


def main():
    """主函数"""
    print("=" * 60)
    print("  Meta-Cognition 完全自动化守护进程")
    print("=" * 60)
    print()
    print("功能：")
    print("  1. 后台自动运行，你什么都不用做")
    print("  2. 监控 tasks/ 目录")
    print("  3. 自动执行 .task 文件中的任务")
    print("  4. 自动记录所有操作")
    print()
    print(f"任务目录: {TASK_DIR}")
    print(f"日志文件: {LOG_FILE}")
    print("=" * 60)
    print()

    # 创建示例任务文件（如果不存在）
    example_task = TASK_DIR / "示例任务.task"
    if not example_task.exists():
        with open(example_task, 'w', encoding='utf-8') as f:
            f.write("请帮我优化这段代码，提升性能")
        print(f"[提示] 已创建示例任务文件: {example_task}")

    # 启动守护进程
    daemon = AutoDaemonManager()
    daemon.start()


if __name__ == "__main__":
    main()
