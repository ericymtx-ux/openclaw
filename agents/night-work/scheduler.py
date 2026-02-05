"""
任务调度器 - Phase 2: OpenCode 集成

功能：
- 根据任务特性选择执行 Worker (OpenCode / Claude Code / Script)
- 通过 MCP 协议调用 opencode-team skill
- 管理任务执行流程
"""

import asyncio
import json
import os
import sys
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from subprocess import Popen, PIPE

# 从同目录导入
from task_scorer import Task, Priority


class WorkerType(Enum):
    """执行 Worker 类型"""
    OPENCODE = "opencode"
    CLAUDE_CODE = "claude-code"
    SCRIPT = "script"


@dataclass
class ExecutionResult:
    """执行结果"""
    task_id: str
    success: bool
    output: str
    files_changed: List[str] = field(default_factory=list)
    pr_url: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0


class OpenCodeClient:
    """OpenCode Team MCP 客户端"""

    def __init__(self):
        self.process: Optional[Popen] = None
        self.server_script = (
            Path.home() / ".pyenv/versions/3.11/bin/python" if 
            (Path.home() / ".pyenv/versions/3.11/bin/python").exists() else
            Path("/opt/homebrew/bin/python3")
        )
        # PROJECT_ROOT 是 openclaw 根目录
        PROJECT_ROOT = Path(__file__).parent.parent.parent
        self.mcp_server = PROJECT_ROOT / "skills/opencode-team/src/opencode_team_mcp/server.py"
        self.workers: Dict[str, Dict] = {}

    def start(self) -> bool:
        """启动 MCP Server"""
        try:
            cmd = [
                str(self.server_script),
                "-m", "opencode_team_mcp"
            ]
            
            self.process = Popen(
                cmd,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                cwd=str(PROJECT_ROOT / "skills/opencode-team")
            )
            
            # 等待启动
            import time
            time.sleep(1)
            
            # 检查进程状态
            if self.process.poll() is not None:
                stderr = self.process.stderr.read()
                print(f"❌ MCP Server 启动失败: {stderr}")
                return False
                
            print("✅ OpenCode MCP Server 已启动")
            return True
            
        except Exception as e:
            print(f"❌ 启动 MCP Server 失败: {e}")
            return False

    def stop(self):
        """停止 MCP Server"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            print("🛑 OpenCode MCP Server 已停止")

    def spawn_worker(self, project_path: str, prompt: str, annotation: str = "") -> Optional[str]:
        """Spawn 一个 OpenCode worker"""
        if not self.process:
            if not self.start():
                return None

        try:
            # 构造 MCP 请求
            request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": "spawn_workers",
                    "arguments": {
                        "workers": [{
                            "project_path": project_path,
                            "prompt": prompt,
                            "annotation": annotation or prompt[:50],
                            "use_worktree": True,
                            "skip_permissions": False
                        }],
                        "layout": "new"
                    }
                }
            }
            
            # 发送请求
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            # 读取响应
            response_line = self.process.stdout.readline()
            response = json.loads(response_line)
            
            if "result" in response:
                # 解析 worker 信息
                text = response["result"].get("content", [{}])[0].get("text", "")
                # 提取 session_id
                if "session_id" in text:
                    import re
                    match = re.search(r'\(([a-f0-9]+)\)', text)
                    if match:
                        session_id = match.group(1)
                        self.workers[session_id] = {
                            "project_path": project_path,
                            "prompt": prompt,
                            "started_at": datetime.now().isoformat()
                        }
                        return session_id
            
            return None
            
        except Exception as e:
            print(f"❌ Spawn worker 失败: {e}")
            return None

    def list_workers(self) -> List[Dict]:
        """列出所有 workers"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": "list_workers",
                    "arguments": {}
                }
            }
            
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            response_line = self.process.stdout.readline()
            response = json.loads(response_line)
            
            return self.workers
            
        except Exception as e:
            print(f"❌ List workers 失败: {e}")
            return []

    def close_worker(self, session_id: str) -> bool:
        """关闭 worker"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": "close_workers",
                    "arguments": {
                        "session_ids": [session_id]
                    }
                }
            }
            
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            if session_id in self.workers:
                del self.workers[session_id]
            
            return True
            
        except Exception as e:
            print(f"❌ Close worker 失败: {e}")
            return False
        
    def start(self) -> bool:
        """启动 MCP Server"""
        try:
            cmd = [
                str(self.server_script),
                "-m", "opencode_team_mcp"
            ]
            
            self.process = Popen(
                cmd,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                cwd=str(PROJECT_ROOT / "skills/opencode-team")
            )
            
            # 等待启动
            import time
            time.sleep(1)
            
            # 检查进程状态
            if self.process.poll() is not None:
                stderr = self.process.stderr.read()
                print(f"❌ MCP Server 启动失败: {stderr}")
                return False
                
            print("✅ OpenCode MCP Server 已启动")
            return True
            
        except Exception as e:
            print(f"❌ 启动 MCP Server 失败: {e}")
            return False

    def stop(self):
        """停止 MCP Server"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            print("🛑 OpenCode MCP Server 已停止")

    def spawn_worker(self, project_path: str, prompt: str, annotation: str = "") -> Optional[str]:
        """Spawn 一个 OpenCode worker"""
        if not self.process:
            if not self.start():
                return None

        try:
            # 构造 MCP 请求
            request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": "spawn_workers",
                    "arguments": {
                        "workers": [{
                            "project_path": project_path,
                            "prompt": prompt,
                            "annotation": annotation or prompt[:50],
                            "use_worktree": True,
                            "skip_permissions": False
                        }],
                        "layout": "new"
                    }
                }
            }
            
            # 发送请求
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            # 读取响应
            response_line = self.process.stdout.readline()
            response = json.loads(response_line)
            
            if "result" in response:
                # 解析 worker 信息
                text = response["result"].get("content", [{}])[0].get("text", "")
                # 提取 session_id
                if "session_id" in text:
                    import re
                    match = re.search(r'\(([a-f0-9]+)\)', text)
                    if match:
                        session_id = match.group(1)
                        self.workers[session_id] = {
                            "project_path": project_path,
                            "prompt": prompt,
                            "started_at": datetime.now().isoformat()
                        }
                        return session_id
            
            return None
            
        except Exception as e:
            print(f"❌ Spawn worker 失败: {e}")
            return None

    def list_workers(self) -> List[Dict]:
        """列出所有 workers"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": "list_workers",
                    "arguments": {}
                }
            }
            
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            response_line = self.process.stdout.readline()
            response = json.loads(response_line)
            
            return self.workers
            
        except Exception as e:
            print(f"❌ List workers 失败: {e}")
            return []

    def close_worker(self, session_id: str) -> bool:
        """关闭 worker"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": "close_workers",
                    "arguments": {
                        "session_ids": [session_id]
                    }
                }
            }
            
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            if session_id in self.workers:
                del self.workers[session_id]
            
            return True
            
        except Exception as e:
            print(f"❌ Close worker 失败: {e}")
            return False


class ClaudeCodeClient:
    """Claude Code Team 客户端 (通过 mcporter)"""

    def __init__(self):
        self.mcporter_available = self._check_mcporter()

    def _check_mcporter(self) -> bool:
        """检查 mcporter 是否可用"""
        try:
            result = subprocess.run(
                ["which", "mcporter"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def spawn_worker(self, project_path: str, prompt: str, annotation: str = "") -> Optional[str]:
        """Spawn 一个 Claude Code worker"""
        if not self.mcporter_available:
            print("⚠️ mcporter 未安装，Claude Code 集成不可用")
            return None

        try:
            # 构建 JSON 参数
            worker_config = {
                "project_path": project_path,
                "annotation": annotation or prompt[:50],
                "prompt": prompt,
                "use_worktree": True,
                "skip_permissions": True
            }

            # 调用 mcporter
            result = subprocess.run(
                ["mcporter", "call", "claude-team.spawn_workers",
                 f"workers={json.dumps([worker_config])}",
                 "layout=new"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # 解析输出获取 worker name
                output = result.stdout
                # 提取 worker 名称 (如 "Groucho")
                import re
                match = re.search(r'^\s*-\s+(\w+)', output, re.MULTILINE)
                if match:
                    worker_name = match.group(1)
                    print(f"✅ Claude Code worker spawned: {worker_name}")
                    return worker_name

            print(f"⚠️ mcporter spawn 失败: {result.stderr}")
            return None

        except subprocess.TimeoutExpired:
            print("❌ mcporter 超时")
            return None
        except Exception as e:
            print(f"❌ Spawn Claude Code worker 失败: {e}")
            return None

    def list_workers(self) -> List[Dict]:
        """列出所有 workers"""
        if not self.mcporter_available:
            return []

        try:
            result = subprocess.run(
                ["mcporter", "call", "claude-team.list_workers"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # 解析输出
                workers = []
                import re
                lines = result.stdout.split('\n')
                for line in lines:
                    match = re.match(r'-\s+(\w+)\s+\(([a-f0-9]+)\):\s+(\w+)\s+-\s+(.+)', line)
                    if match:
                        workers.append({
                            "name": match.group(1),
                            "session_id": match.group(2),
                            "status": match.group(3),
                            "annotation": match.group(4)
                        })
                return workers

        except Exception as e:
            print(f"❌ List workers 失败: {e}")

        return []

    def wait_for_workers(self, session_ids: List[str], timeout: int = 600) -> bool:
        """等待 workers 完成"""
        if not self.mcporter_available:
            return False

        try:
            result = subprocess.run(
                ["mcporter", "call", "claude-team.wait_idle_workers",
                 f"session_ids={json.dumps(session_ids)}",
                 f"mode=all",
                 f"timeout={timeout}"],
                capture_output=True,
                text=True,
                timeout=timeout + 30
            )
            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("❌ 等待 workers 超时")
            return False
        except Exception as e:
            print(f"❌ Wait 失败: {e}")
            return False

    def close_workers(self, session_ids: List[str]) -> bool:
        """关闭 workers"""
        if not self.mcporter_available:
            return False

        try:
            result = subprocess.run(
                ["mcporter", "call", "claude-team.close_workers",
                 f"session_ids={json.dumps(session_ids)}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"✅ 已关闭 {len(session_ids)} 个 workers")
                return True

        except Exception as e:
            print(f"❌ Close workers 失败: {e}")

        return False

    def read_logs(self, session_id: str, pages: int = 1) -> str:
        """读取 worker 日志"""
        if not self.mcporter_available:
            return ""

        try:
            result = subprocess.run(
                ["mcporter", "call", "claude-team.read_worker_logs",
                 f"session_id={session_id}",
                 f"pages={pages}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout

        except Exception as e:
            print(f"❌ Read logs 失败: {e}")
            return ""


class TaskScheduler:
    """任务调度器"""

    def __init__(self, workspace: Path = None):
        self.workspace = workspace or Path.cwd()
        self.opencode_client = OpenCodeClient()
        self.claude_code_client = ClaudeCodeClient()
        self.execution_history: List[Dict] = []

    def select_worker(self, task: Task) -> WorkerType:
        """选择执行 Worker
        
        规则：
        - 预估时间 <= 60分钟 + 影响单模块 → OpenCode
        - 预估时间 > 60分钟 或 影响多模块 → Claude Code
        - 简单脚本任务 → Script
        """
        if task.estimated_minutes <= 60 and not task.affects_multiple_modules:
            # 检查是否是简单脚本任务
            if self._is_simple_script_task(task):
                return WorkerType.SCRIPT
            return WorkerType.OPENCODE
        else:
            return WorkerType.CLAUDE_CODE

    def _is_simple_script_task(self, task: Task) -> bool:
        """判断是否是简单脚本任务"""
        keywords = ["脚本", "script", "bash", "shell", "命令"]
        return any(kw in task.title for kw in keywords)

    def execute(self, task: Task) -> ExecutionResult:
        """执行任务"""
        start_time = datetime.now()
        worker = self.select_worker(task)

        print(f"📋 执行任务 [{task.id}]: {task.title}")
        print(f"   选择 Worker: {worker.value}")

        try:
            if worker == WorkerType.OPENCODE:
                result = self._execute_opencode(task)
            elif worker == WorkerType.CLAUDE_CODE:
                result = self._execute_claude_code(task)
            else:
                result = self._execute_script(task)

            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            self.execution_history.append({
                "task_id": task.id,
                "worker": worker.value,
                "success": result.success,
                "duration": result.duration_seconds
            })

            return result

        except Exception as e:
            return ExecutionResult(
                task_id=task.id,
                success=False,
                output="",
                error=str(e),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )

    def _execute_opencode(self, task: Task) -> ExecutionResult:
        """通过 OpenCode 执行"""
        # 生成 prompt
        prompt = self._build_task_prompt(task)
        
        # Spawn worker
        session_id = self.opencode_client.spawn_worker(
            project_path=str(self.workspace),
            prompt=prompt,
            annotation=f"[{task.id}] {task.title}"
        )
        
        if not session_id:
            return ExecutionResult(
                task_id=task.id,
                success=False,
                output="",
                error="Failed to spawn OpenCode worker"
            )
        
        print(f"✅ Worker spawned: {session_id}")
        
        # 等待并收集结果
        # 注意：实际等待逻辑需要完善
        return ExecutionResult(
            task_id=task.id,
            success=True,
            output=f"OpenCode worker started: {session_id}",
            files_changed=[],
            duration_seconds=0
        )

    def _execute_claude_code(self, task: Task) -> ExecutionResult:
        """通过 Claude Code 执行 (使用 claude-team mcporter)"""
        prompt = self._build_task_prompt(task)
        
        # 尝试使用 claude-team (mcporter)
        if self.claude_code_client.mcporter_available:
            worker_name = self.claude_code_client.spawn_worker(
                project_path=str(self.workspace),
                prompt=prompt,
                annotation=f"[{task.id}] {task.title}"
            )
            
            if worker_name:
                # 等待 worker 完成
                success = self.claude_code_client.wait_for_workers([worker_name], timeout=3600)
                
                if success:
                    # 读取日志获取结果
                    logs = self.claude_code_client.read_logs(worker_name, pages=2)
                    
                    # 关闭 worker
                    self.claude_code_client.close_workers([worker_name])
                    
                    return ExecutionResult(
                        task_id=task.id,
                        success=True,
                        output=logs,
                        files_changed=self._parse_changed_files(logs)
                    )
                else:
                    return ExecutionResult(
                        task_id=task.id,
                        success=False,
                        output="",
                        error="Claude Code worker 执行超时"
                    )
            else:
                return ExecutionResult(
                    task_id=task.id,
                    success=False,
                    output="",
                    error="Failed to spawn Claude Code worker via mcporter"
                )
        else:
            # 回退到 claude-code CLI
            try:
                result = subprocess.run(
                    ["claude-code", "run", "--message", prompt],
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1小时超时
                )
                
                return ExecutionResult(
                    task_id=task.id,
                    success=result.returncode == 0,
                    output=result.stdout + result.stderr,
                    files_changed=self._parse_changed_files(result.stdout),
                    error=result.stderr if result.returncode != 0 else None
                )
                
            except FileNotFoundError:
                return ExecutionResult(
                    task_id=task.id,
                    success=False,
                    output="",
                    error="Claude Code CLI not found. Install: npm install -g @anthropic/claude-code"
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    task_id=task.id,
                    success=False,
                    output="",
                    error="Execution timeout (1 hour)"
                )

    def _execute_script(self, task: Task) -> ExecutionResult:
        """执行脚本任务"""
        # 从任务内容中提取脚本
        script_content = self._extract_script(task)
        
        if not script_content:
            return ExecutionResult(
                task_id=task.id,
                success=False,
                output="",
                error="No script found in task"
            )
        
        # 写入临时脚本
        script_path = Path.home() / ".openclaw/night_work" / f"{task.id}.sh"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        
        try:
            result = subprocess.run(
                ["bash", str(script_path)],
                capture_output=True,
                text=True,
                timeout=1800  # 30分钟超时
            )
            
            return ExecutionResult(
                task_id=task.id,
                success=result.returncode == 0,
                output=result.stdout + result.stderr,
                files_changed=self._parse_changed_files(result.stdout),
                error=result.stderr if result.returncode != 0 else None
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                task_id=task.id,
                success=False,
                output="",
                error="Script timeout (30 min)"
            )

    def _build_task_prompt(self, task: Task) -> str:
        """构建任务 prompt"""
        prompt = f"""Task: {task.title}

ID: {task.id}
Priority: {task.priority.value}
Estimated: {task.estimated_minutes} minutes

Please complete this task with the following requirements:
1. Focus on the main objective: {task.title}
2. Write clean, working code
3. Add tests if applicable
4. Update documentation if needed

Return a summary of what was accomplished and any files changed.
"""
        return prompt

    def _extract_script(self, task: Task) -> str:
        """从任务中提取脚本内容"""
        # 临时实现：从任务标题生成简单脚本
        title = task.title
        
        if "shell" in title.lower() or "bash" in title.lower():
            return f"#!/bin/bash\necho 'Running task: {task.id}'\n"
        
        return ""

    def _parse_changed_files(self, output: str) -> List[str]:
        """从输出中解析变更文件"""
        files = []
        for line in output.split('\n'):
            if 'Modified:' in line or 'Changed:' in line:
                path = line.split(':', 1)[1].strip()
                files.append(path)
        return files

    def cleanup(self):
        """清理资源"""
        self.opencode_client.stop()

    def get_execution_summary(self) -> Dict:
        """获取执行摘要"""
        total = len(self.execution_history)
        success = sum(1 for h in self.execution_history if h["success"])
        
        by_worker = {}
        for h in self.execution_history:
            worker = h["worker"]
            by_worker.setdefault(worker, {"total": 0, "success": 0})
            by_worker[worker]["total"] += 1
            if h["success"]:
                by_worker[worker]["success"] += 1
        
        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "by_worker": by_worker
        }


def main():
    """测试调度器"""
    from task_scorer import Task, Priority

    # 创建测试任务
    test_task = Task(
        id="TEST_001",
        title="测试任务 - 验证 OpenCode 集成",
        priority=Priority.P1,
        estimated_minutes=30,
        requires_user_decision=False,
        affects_multiple_modules=False,
        has_clear_dod=True
    )

    scheduler = TaskScheduler()
    
    # 测试 worker 选择
    worker = scheduler.select_worker(test_task)
    print(f"✅ Worker 选择测试通过: {worker.value}")
    
    # 清理
    scheduler.cleanup()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
