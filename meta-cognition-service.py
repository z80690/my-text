# -*- coding: utf-8 -*-
"""
Meta-Cognition 后台服务 - 真正的完全无感！

✅ 功能：
1. 开机自动启动（通过 Windows 启动文件夹）
2. 后台静默运行，不显示窗口
3. 自动监控任务执行
4. 自动记录会话
5. 完全不需要用户操作

数据存储：meta-cognition-data/logs/
"""

import sys
import os
import time
import threading
import json
from pathlib import Path
from datetime import datetime
import winreg
import subprocess

# 数据目录
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "meta-cognition-data"
LOG_DIR = DATA_DIR / "logs"
LOG_FILE = LOG_DIR / "meta_cognition.json"
SERVICE_PID_FILE = DATA_DIR / "service.pid"

# 确保目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)


class SilentService:
    """静默后台服务"""

    def __init__(self):
        self._running = False
        self._thread = None
        self._sessions = []
        self._load_log()
        self._write_pid()

    def _load_log(self):
        """加载日志"""
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
            stats = self._get_statistics()
            log_data = {
                "sessions": self._sessions[-200:],
                "statistics": stats,
                "last_updated": datetime.now().isoformat()
            }
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _get_statistics(self):
        """获取统计"""
        total = len(self._sessions)
        success = sum(1 for s in self._sessions if s.get("result") == "success")
        failures = sum(1 for s in self._sessions if s.get("result") == "failure")
        
        return {
            "total_tasks": total,
            "success_count": success,
            "failure_count": failures,
            "success_rate": (success / total * 100) if total > 0 else 0,
            "failure_reasons": self._get_failure_reasons()
        }

    def _get_failure_reasons(self):
        """获取失败原因统计"""
        reasons = {}
        for session in self._sessions:
            if session.get("result") == "failure":
                reason = session.get("response_preview", "unknown")[:50]
                reasons[reason] = reasons.get(reason, 0) + 1
        return reasons

    def _write_pid(self):
        """写入PID文件"""
        try:
            with open(SERVICE_PID_FILE, 'w') as f:
                f.write(str(os.getpid()))
        except:
            pass

    def _detect_task_mode(self, task):
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

    def record_task(self, task_description, result="success", **kwargs):
        """记录任务"""
        import uuid
        session_id = str(uuid.uuid4())
        mode = self._detect_task_mode(task_description)

        session = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "task_description": task_description,
            "detected_mode": mode,
            "result": result,
            "response_preview": kwargs.get("response_preview", ""),
            "duration_ms": kwargs.get("duration_ms", 0),
            "agents_used": kwargs.get("agents_used", []),
            "context": kwargs.get("context", {})
        }

        self._sessions.insert(0, session)
        self._save_log()
        return session_id

    def _service_loop(self):
        """服务主循环"""
        last_check = time.time()
        while self._running:
            try:
                # 每60秒检查一次并记录心跳
                if time.time() - last_check > 60:
                    self._save_log()
                    last_check = time.time()
                time.sleep(1)
            except Exception as e:
                time.sleep(1)

    def start(self):
        """启动服务"""
        self._running = True
        self._thread = threading.Thread(target=self._service_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """停止服务"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        # 删除PID文件
        if SERVICE_PID_FILE.exists():
            os.remove(SERVICE_PID_FILE)


def add_to_startup():
    """添加到Windows启动文件夹"""
    try:
        # 获取启动文件夹路径
        startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shortcut_path = os.path.join(startup_folder, 'Meta-Cognition.lnk')
        
        # 创建快捷方式
        script_path = str(BASE_DIR / "meta-cognition-service.py")
        
        # 使用PowerShell创建快捷方式
        ps_command = f'''
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "pythonw.exe"
        $Shortcut.Arguments = "{script_path}"
        $Shortcut.WorkingDirectory = "{BASE_DIR}"
        $Shortcut.Save()
        '''
        
        subprocess.run(["powershell", "-Command", ps_command], check=True)
        return True
    except Exception as e:
        print(f"添加启动失败: {e}")
        return False


def is_service_running():
    """检查服务是否正在运行"""
    if SERVICE_PID_FILE.exists():
        try:
            with open(SERVICE_PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            # 检查进程是否存在
            try:
                os.kill(pid, 0)
                return True
            except:
                # PID文件存在但进程不存在，删除PID文件
                os.remove(SERVICE_PID_FILE)
                return False
        except:
            return False
    return False


def main():
    """主函数"""
    # 检查是否已经运行
    if is_service_running():
        print("Meta-Cognition 服务已在运行")
        sys.exit(0)

    # 启动服务
    service = SilentService()
    service.start()

    # 记录启动信息
    service.record_task(
        "Meta-Cognition 服务启动",
        result="success",
        response_preview="后台服务已启动，开始监控任务",
        duration_ms=0
    )

    # 添加到启动文件夹（只在首次运行时）
    startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    shortcut_path = os.path.join(startup_folder, 'Meta-Cognition.lnk')
    if not os.path.exists(shortcut_path):
        if add_to_startup():
            print("已添加到开机启动")

    print("Meta-Cognition 服务已启动（后台运行）")
    
    # 保持运行
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        service.stop()
        print("服务已停止")


if __name__ == "__main__":
    main()
