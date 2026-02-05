#!/usr/bin/env python3
"""
OpenCode Team MCP Server - iTerm2 Terminal Integration

Manages OpenCode workers via iTerm2 terminal sessions.
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp import types

# Constants
DEFAULT_LOG_DIR = Path.home() / ".opencode-team" / "logs"
DEFAULT_MEMORY_DIR = Path.home() / ".opencode-team" / "memory"

# Worker names
WORKER_NAMES = [
    "Groucho", "Harpo", "Chico", "Zeppo", "Gummo",
    "Aragorn", "Gandalf", "Legolas", "Gimli", "Frodo",
    "Merry", "Pippin", "Samwise", "Boromir", "Gollum"
]

# Global state
workers: dict[str, dict] = {}
worker_counter = 0
iterm_connection = None
iterm_app = None


def ensure_dirs():
    """Ensure required directories exist."""
    DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def save_worker_state():
    """Save worker state to persistent storage."""
    state_file = DEFAULT_MEMORY_DIR / "worker-tracking.json"
    state = {
        "workers": workers,
        "last_updated": datetime.utcnow().isoformat()
    }
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2, default=str)


def get_worker_name(index: int = 0) -> str:
    """Get a themed worker name."""
    return WORKER_NAMES[index % len(WORKER_NAMES)]


# iTerm2 connection management
async def get_iterm_connection():
    """Get or create iTerm2 connection."""
    global iterm_connection, iterm_app
    
    if iterm_app is not None:
        return iterm_app
    
    try:
        import iterm2
        connection = await iterm2.Connection.async_create()
        app = await iterm2.app.async_get_app(connection)
        if app is None:
            print("Warning: iTerm2 is not running", file=sys.stderr)
            return None
        iterm_connection = connection
        iterm_app = app
        print("Connected to iTerm2", file=sys.stderr)
        return app
    except Exception as e:
        print(f"Warning: Could not connect to iTerm2: {e}", file=sys.stderr)
        return None


async def create_iterm_window(name: str) -> Optional[dict]:
    """Create a new iTerm2 window and return session info."""
    global iterm_connection
    
    if iterm_connection is None:
        try:
            import iterm2
            iterm_connection = await iterm2.Connection.async_create()
        except Exception as e:
            print(f"Warning: Could not connect to iTerm2: {e}", file=sys.stderr)
            return None
    
    try:
        import iterm2
        from iterm2.window import Window
        
        window = await Window.async_create(iterm_connection)
        if window is None:
            raise RuntimeError("Failed to create iTerm2 window")
        
        # Get the first tab and its session
        if window.tabs:
            tab = window.tabs[0]
            
            # Set title
            if name:
                try:
                    await tab.async_set_title(name)
                except:
                    pass
            
            # Get session
            if tab.sessions:
                session = tab.sessions[0]
                return {
                    "window_id": window.window_id,
                    "tab_id": tab.tab_id,
                    "session_id": session.session_id
                }
        
        return {
            "window_id": window.window_id,
            "tab_id": None,
            "session_id": None
        }
    except Exception as e:
        print(f"Error creating iTerm2 window: {e}", file=sys.stderr)
        return None


async def send_text_to_session(session, text: str) -> bool:
    """Send text to an iTerm2 session."""
    try:
        await session.async_send_text(text)
        return True
    except Exception as e:
        print(f"Error sending text: {e}", file=sys.stderr)
        return False


# Create MCP server
app = Server("opencode-team")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="spawn_workers",
            description="Create new OpenCode worker sessions in iTerm2",
            inputSchema={
                "type": "object",
                "properties": {
                    "workers": {
                        "type": "array",
                        "description": "Workers to spawn",
                        "items": {
                            "type": "object",
                            "properties": {
                                "project_path": {"type": "string", "description": "Project directory (or 'auto')"},
                                "annotation": {"type": "string", "description": "Task description"},
                                "prompt": {"type": "string", "description": "Initial prompt"},
                                "use_worktree": {"type": "boolean", "default": True},
                                "skip_permissions": {"type": "boolean", "default": False}
                            },
                            "required": ["project_path"]
                        }
                    },
                    "layout": {"type": "string", "enum": ["auto", "new"], "default": "auto"}
                },
                "required": ["workers"]
            }
        ),
        Tool(
            name="list_workers",
            description="List all managed workers",
            inputSchema={
                "type": "object",
                "properties": {
                    "status_filter": {"type": "string", "enum": ["spawning", "ready", "busy", "closed"]}
                }
            }
        ),
        Tool(
            name="message_workers",
            description="Send messages to workers",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_ids": {"type": "array", "items": {"type": "string"}},
                    "message": {"type": "string"}
                },
                "required": ["session_ids", "message"]
            }
        ),
        Tool(
            name="check_idle_workers",
            description="Check which workers are idle",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_ids": {"type": "array", "items": {"type": "string"}}
                }
            }
        ),
        Tool(
            name="close_workers",
            description="Terminate worker sessions",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_ids": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["session_ids"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Optional[dict] = None) -> types.CallToolResult:
    """Handle tool calls."""
    global worker_counter
    
    if arguments is None:
        arguments = {}
    
    if name == "spawn_workers":
        workers_list = arguments.get("workers", [])
        layout = arguments.get("layout", "auto")
        
        results = []
        for i, worker_config in enumerate(workers_list):
            project_path = worker_config.get("project_path", ".")
            if project_path == "auto":
                project_path = os.environ.get("OPENCODE_TEAM_PROJECT_DIR", ".")
            
            worker_counter += 1
            session_id = str(uuid.uuid4())[:8]
            worker_name = get_worker_name(worker_counter)
            
            # Try to create iTerm2 window
            iterm_info = None
            try:
                iterm_info = await create_iterm_window(worker_name)
                print(f"Created iTerm2 window: {iterm_info}", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Could not create iTerm2 window: {e}", file=sys.stderr)
            
            worker = {
                "session_id": session_id,
                "name": worker_name,
                "project_path": project_path,
                "prompt": worker_config.get("prompt", ""),
                "annotation": worker_config.get("annotation", "") or worker_config.get("prompt", "")[:50],
                "status": "ready",
                "use_worktree": worker_config.get("use_worktree", True),
                "skip_permissions": worker_config.get("skip_permissions", False),
                "started_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "iterm": iterm_info
            }
            
            workers[session_id] = worker
            results.append(worker)
            
            # Send commands to iTerm2 if available
            if iterm_info and iterm_info.get("session_id"):
                try:
                    import iterm2
                    # Find the session and send text
                    app = await iterm2.app.async_get_app(iterm_connection)
                    if app:
                        for window in app.terminal_windows:
                            for tab in window.tabs:
                                for session in tab.sessions:
                                    if session.session_id == iterm_info["session_id"]:
                                        # Send cd command
                                        await session.async_send_text(f"cd {project_path}\n")
                                        # Send opencode run command with prompt
                                        prompt = worker.get("prompt", "")
                                        if prompt:
                                            # Escape quotes in prompt
                                            escaped_prompt = prompt.replace('"', '\\"')
                                            cmd = f'opencode run "{escaped_prompt}"'
                                        else:
                                            cmd = "opencode"
                                        
                                        await session.async_send_text(cmd + "\n")
                                        break
                except Exception as e:
                    print(f"Error sending to iTerm2: {e}", file=sys.stderr)
        
        save_worker_state()
        
        return types.CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Spawned {len(results)} workers:\n" + 
                     "\n".join([f"- {w['name']} ({w['session_id']}): {w['annotation']}" for w in results])
            )]
        )
    
    elif name == "list_workers":
        status_filter = arguments.get("status_filter")
        all_workers = list(workers.values())
        
        # Remove duplicates by session_id
        seen = set()
        unique_workers = []
        for w in all_workers:
            if w["session_id"] not in seen:
                seen.add(w["session_id"])
                unique_workers.append(w)
        
        if status_filter:
            unique_workers = [w for w in unique_workers if w.get("status") == status_filter]
        
        if not unique_workers:
            return types.CallToolResult(
                content=[TextContent(type="text", text="No workers found")]
            )
        
        lines = [f"Workers ({len(unique_workers)}):\n"]
        for w in unique_workers:
            lines.append(f"- {w['name']} ({w['session_id']}): {w['status']} - {w['annotation']}")
        
        return types.CallToolResult(
            content=[TextContent(type="text", text="\n".join(lines))]
        )
    
    elif name == "message_workers":
        session_ids = arguments.get("session_ids", [])
        message = arguments.get("message", "")
        
        found = []
        for sid in session_ids:
            if sid in workers:
                workers[sid]["last_activity"] = datetime.utcnow().isoformat()
                workers[sid]["status"] = "busy"
                workers[sid]["pending_message"] = message
                found.append(workers[sid]["name"])
        
        save_worker_state()
        
        return types.CallToolResult(
            content=[TextContent(type="text", text=f"Message queued for {len(found)} workers: {', '.join(found)}")]
        )
    
    elif name == "check_idle_workers":
        session_ids = arguments.get("session_ids", [])
        
        idle = []
        for sid in session_ids:
            if sid in workers and workers[sid].get("status") in ["ready", "idle"]:
                idle.append(workers[sid])
        
        return types.CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Idle workers: {len(idle)}\n" + 
                     "\n".join([f"- {w['name']}" for w in idle])
            )]
        )
    
    elif name == "close_workers":
        session_ids = arguments.get("session_ids", [])
        
        closed = []
        for sid in session_ids:
            if sid in workers:
                workers[sid]["status"] = "closed"
                workers[sid]["closed_at"] = datetime.utcnow().isoformat()
                closed.append(workers[sid]["name"])
        
        save_worker_state()
        
        return types.CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Closed {len(closed)} workers: {', '.join(closed)}\n\n"
                     "Worktree cleanup: Review commits and merge/cherry-pick to main branch."
            )]
        )
    
    return types.CallToolResult(
        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
    )


async def run():
    """Run the MCP server."""
    ensure_dirs()
    
    # Load persisted state
    state_file = DEFAULT_MEMORY_DIR / "worker-tracking.json"
    if state_file.exists():
        try:
            with open(state_file, 'r') as f:
                data = json.load(f)
                for sid, info in data.get("workers", {}).items():
                    if info.get("status") != "closed":
                        workers[sid] = info
        except:
            pass
    
    # Run stdio server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenCode Team MCP Server")
    parser.add_argument("--version", action="store_true", help="Show version")
    
    args = parser.parse_args()
    
    if args.version:
        print("opencode-team MCP server v0.1.0")
        return
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
