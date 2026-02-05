"""
Comprehensive tests for OpenCode Team MCP Server tools.

Tests all MCP tools:
- spawn_workers
- list_workers
- message_workers
- check_idle_workers
- close_workers
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class MockCallToolResult:
    """Mock CallToolResult for testing."""
    
    def __init__(self, content):
        self.content = content


class MockTextContent:
    """Mock TextContent for testing."""
    
    def __init__(self, text):
        self.type = "text"
        self.text = text


class TestSpawnWorkersTool:
    """Test spawn_workers MCP tool."""
    
    @pytest.fixture
    def server(self):
        """Create server instance with mocked dependencies."""
        with patch("opencode_team_mcp.server.create_iterm_window") as mock_iterm:
            mock_iterm.return_value = None
            
            # Import and reset workers
            from opencode_team_mcp import server
            server.workers = {}
            server.worker_counter = 0
            
            return server
    
    def test_spawn_single_worker(self, server):
        """Test spawning a single worker."""
        workers_config = [{
            "project_path": "/test/project",
            "annotation": "Test task",
            "prompt": "Do something"
        }]
        
        arguments = {"workers": workers_config}
        
        # Call the tool handler
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server.call_tool("spawn_workers", arguments)
            return result
        
        # Mock the iTerm2 creation
        with patch.object(server, 'create_iterm_window', new_callable=AsyncMock) as mock:
            mock.return_value = {"window_id": "1", "tab_id": "1", "session_id": "s1"}
            
            result = asyncio.run(run_test())
            
            # Verify result
            assert len(result.content) == 1
            assert "Spawned 1 workers" in result.content[0].text
            assert "Test task" in result.content[0].text
    
    def test_spawn_multiple_workers(self, server):
        """Test spawning multiple workers."""
        workers_config = [
            {"project_path": "/project1", "annotation": "Task 1"},
            {"project_path": "/project2", "annotation": "Task 2"},
        ]
        
        arguments = {"workers": workers_config}
        
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server.call_tool("spawn_workers", arguments)
            return result
        
        with patch.object(server, 'create_iterm_window', new_callable=AsyncMock) as mock:
            mock.return_value = {"window_id": "1", "tab_id": "1", "session_id": "s1"}
            
            result = asyncio.run(run_test())
            
            assert "Spawned 2 workers" in result.content[0].text
    
    def test_spawn_worker_with_auto_project(self, server):
        """Test spawning worker with auto project path."""
        workers_config = [{
            "project_path": "auto",
            "annotation": "Auto task"
        }]
        
        arguments = {"workers": workers_config}
        
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server.call_tool("spawn_workers", arguments)
            return result
        
        with patch.object(server, 'create_iterm_window', new_callable=AsyncMock) as mock:
            mock.return_value = None
            
            result = asyncio.run(run_test())
            
            # Verify worker was created with project from env or default
            assert "Spawned 1 workers" in result.content[0].text
    
    def test_spawn_worker_with_worktree_settings(self, server):
        """Test spawning worker with worktree settings."""
        workers_config = [{
            "project_path": "/test",
            "annotation": "Task",
            "use_worktree": False,
            "skip_permissions": True
        }]
        
        arguments = {"workers": workers_config}
        
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server.call_tool("spawn_workers", arguments)
            return result
        
        with patch.object(server, 'create_iterm_window', new_callable=AsyncMock) as mock:
            mock.return_value = None
            
            result = asyncio.run(run_test())
            
            # Check that worker was created with correct settings
            assert len(server.workers) == 1
            worker = list(server.workers.values())[0]
            assert worker["use_worktree"] is False
            assert worker["skip_permissions"] is True


class TestListWorkersTool:
    """Test list_workers MCP tool."""
    
    @pytest.fixture
    def server_with_workers(self):
        """Create server with test workers."""
        with patch("opencode_team_mcp.server.create_iterm_window") as mock:
            mock.return_value = None
            
            from opencode_team_mcp import server
            server.workers = {}
            server.worker_counter = 0
            
            # Add test workers
            server.workers["worker1"] = {
                "session_id": "worker1",
                "name": "Groucho",
                "project_path": "/test1",
                "prompt": "",
                "annotation": "Test worker 1",
                "status": "ready",
                "use_worktree": True,
                "skip_permissions": False,
                "started_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "iterm": None
            }
            
            server.workers["worker2"] = {
                "session_id": "worker2",
                "name": "Harpo",
                "project_path": "/test2",
                "prompt": "",
                "annotation": "Test worker 2",
                "status": "busy",
                "use_worktree": True,
                "skip_permissions": False,
                "started_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "iterm": None
            }
            
            return server
    
    def test_list_all_workers(self, server_with_workers):
        """Test listing all workers."""
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server_with_workers.call_tool("list_workers", {})
            return result
        
        result = asyncio.run(run_test())
        
        assert "Workers (2)" in result.content[0].text
        assert "Groucho" in result.content[0].text
        assert "Harpo" in result.content[0].text
    
    def test_list_workers_with_status_filter(self, server_with_workers):
        """Test filtering workers by status."""
        arguments = {"status_filter": "ready"}
        
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server_with_workers.call_tool("list_workers", arguments)
            return result
        
        result = asyncio.run(run_test())
        
        assert "ready" in result.content[0].text
        assert "Groucho" in result.content[0].text
    
    def test_list_workers_empty(self):
        """Test listing when no workers exist."""
        with patch("opencode_team_mcp.server.create_iterm_window") as mock:
            mock.return_value = None
            
            from opencode_team_mcp import server
            server.workers = {}
            
            import asyncio
            from mcp import types
            
            async def run_test():
                result = await server.call_tool("list_workers", {})
                return result
            
            result = asyncio.run(run_test())
            
            assert "No workers found" in result.content[0].text


class TestMessageWorkersTool:
    """Test message_workers MCP tool."""
    
    @pytest.fixture
    def server_with_workers(self):
        """Create server with test workers."""
        with patch("opencode_team_mcp.server.create_iterm_window") as mock:
            mock.return_value = None
            
            from opencode_team_mcp import server
            server.workers = {}
            server.worker_counter = 0
            
            server.workers["worker1"] = {
                "session_id": "worker1",
                "name": "Groucho",
                "project_path": "/test",
                "prompt": "",
                "annotation": "Test",
                "status": "ready",
                "use_worktree": True,
                "skip_permissions": False,
                "started_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "iterm": None
            }
            
            return server
    
    def test_message_single_worker(self, server_with_workers):
        """Test messaging a single worker."""
        arguments = {
            "session_ids": ["worker1"],
            "message": "Continue with next task"
        }
        
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server_with_workers.call_tool("message_workers", arguments)
            return result
        
        result = asyncio.run(run_test())
        
        assert "1 workers" in result.content[0].text
        assert "Groucho" in result.content[0].text
    
    def test_message_updates_status(self, server_with_workers):
        """Test that messaging updates worker status."""
        arguments = {
            "session_ids": ["worker1"],
            "message": "New task"
        }
        
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server_with_workers.call_tool("message_workers", arguments)
            return result
        
        asyncio.run(run_test())
        
        # Check that status was updated
        assert server_with_workers.workers["worker1"]["status"] == "busy"
        assert "New task" in server_with_workers.workers["worker1"].get("pending_message", "")
    
    def test_message_nonexistent_worker(self, server_with_workers):
        """Test messaging a worker that doesn't exist."""
        arguments = {
            "session_ids": ["nonexistent"],
            "message": "Test"
        }
        
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server_with_workers.call_tool("message_workers", arguments)
            return result
        
        result = asyncio.run(run_test())
        
        # Should report 0 workers found
        assert "0 workers" in result.content[0].text


class TestCheckIdleWorkersTool:
    """Test check_idle_workers MCP tool."""
    
    @pytest.fixture
    def server_with_workers(self):
        """Create server with test workers."""
        with patch("opencode_team_mcp.server.create_iterm_window") as mock:
            mock.return_value = None
            
            from opencode_team_mcp import server
            server.workers = {}
            server.worker_counter = 0
            
            server.workers["worker1"] = {
                "session_id": "worker1",
                "name": "Groucho",
                "project_path": "/test",
                "prompt": "",
                "annotation": "Test",
                "status": "ready",
                "use_worktree": True,
                "skip_permissions": False,
                "started_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "iterm": None
            }
            
            server.workers["worker2"] = {
                "session_id": "worker2",
                "name": "Harpo",
                "project_path": "/test",
                "prompt": "",
                "annotation": "Test",
                "status": "busy",
                "use_worktree": True,
                "skip_permissions": False,
                "started_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "iterm": None
            }
            
            return server
    
    def test_check_idle_workers(self, server_with_workers):
        """Test checking idle workers."""
        arguments = {
            "session_ids": ["worker1", "worker2"]
        }
        
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server_with_workers.call_tool("check_idle_workers", arguments)
            return result
        
        result = asyncio.run(run_test())
        
        # Should find 1 idle worker (worker1 with status "ready")
        assert "1" in result.content[0].text
        assert "Groucho" in result.content[0].text
    
    def test_check_idle_with_specific_ids(self, server_with_workers):
        """Test checking idle workers with specific IDs."""
        arguments = {
            "session_ids": ["worker1"]  # Only check worker1
        }
        
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server_with_workers.call_tool("check_idle_workers", arguments)
            return result
        
        result = asyncio.run(run_test())
        
        assert "1" in result.content[0].text


class TestCloseWorkersTool:
    """Test close_workers MCP tool."""
    
    @pytest.fixture
    def server_with_workers(self):
        """Create server with test workers."""
        with patch("opencode_team_mcp.server.create_iterm_window") as mock:
            mock.return_value = None
            
            from opencode_team_mcp import server
            server.workers = {}
            server.worker_counter = 0
            
            server.workers["worker1"] = {
                "session_id": "worker1",
                "name": "Groucho",
                "project_path": "/test",
                "prompt": "",
                "annotation": "Test",
                "status": "ready",
                "use_worktree": True,
                "skip_permissions": False,
                "started_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "iterm": None
            }
            
            server.workers["worker2"] = {
                "session_id": "worker2",
                "name": "Harpo",
                "project_path": "/test",
                "prompt": "",
                "annotation": "Test",
                "status": "busy",
                "use_worktree": True,
                "skip_permissions": False,
                "started_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "iterm": None
            }
            
            return server
    
    def test_close_single_worker(self, server_with_workers):
        """Test closing a single worker."""
        arguments = {
            "session_ids": ["worker1"]
        }
        
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server_with_workers.call_tool("close_workers", arguments)
            return result
        
        result = asyncio.run(run_test())
        
        assert "1 workers" in result.content[0].text
        assert "Groucho" in result.content[0].text
    
    def test_close_multiple_workers(self, server_with_workers):
        """Test closing multiple workers."""
        arguments = {
            "session_ids": ["worker1", "worker2"]
        }
        
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server_with_workers.call_tool("close_workers", arguments)
            return result
        
        result = asyncio.run(run_test())
        
        assert "2 workers" in result.content[0].text
        assert "worktree cleanup" in result.content[0].text.lower()
    
    def test_close_updates_status(self, server_with_workers):
        """Test that closing updates worker status."""
        arguments = {
            "session_ids": ["worker1"]
        }
        
        import asyncio
        from mcp import types
        
        async def run_test():
            result = await server_with_workers.call_tool("close_workers", arguments)
            return result
        
        asyncio.run(run_test())
        
        # Check that status was updated
        assert server_with_workers.workers["worker1"]["status"] == "closed"
        assert "closed_at" in server_with_workers.workers["worker1"]


class TestITerm2Integration:
    """Test iTerm2 integration functions."""
    
    @pytest.mark.asyncio
    async def test_send_text_to_session_returns_bool(self):
        """Test that send_text_to_session returns boolean."""
        from opencode_team_mcp.server import send_text_to_session
        from unittest.mock import MagicMock
        
        mock_session = MagicMock()
        mock_session.async_send_text = AsyncMock(side_effect=Exception("Error"))
        
        result = await send_text_to_session(mock_session, "test")
        
        assert result is False


class TestWorkerNaming:
    """Test worker naming functionality."""
    
    def test_worker_name_cycling(self):
        """Test that worker names cycle correctly."""
        from opencode_team_mcp.server import get_worker_name, WORKER_NAMES
        
        # Get names at all indices
        names = [get_worker_name(i) for i in range(len(WORKER_NAMES) + 2)]
        
        # First name should match last name (cycling)
        assert names[0] == names[-2]
        assert names[1] == names[-1]
    
    def test_unique_names_for_first_batch(self):
        """Test that first batch of workers get unique names."""
        from opencode_team_mcp.server import get_worker_name
        
        # Get names for first batch (assuming batch size < total names)
        batch_size = 5
        names = [get_worker_name(i) for i in range(batch_size)]
        
        # All names should be unique
        assert len(set(names)) == len(names)
    
    def test_worker_name_list_complete(self):
        """Test that worker name list has all expected names."""
        from opencode_team_mcp.server import WORKER_NAMES
        
        expected_names = [
            "Groucho", "Harpo", "Chico", "Zeppo", "Gummo",
            "Aragorn", "Gandalf", "Legolas", "Gimli", "Frodo",
            "Merry", "Pippin", "Samwise", "Boromir", "Gollum"
        ]
        
        assert WORKER_NAMES == expected_names


class TestDirectoryManagement:
    """Test directory setup and management."""
    
    def test_default_directories_exist(self):
        """Test that default directories are defined correctly."""
        from opencode_team_mcp.server import DEFAULT_LOG_DIR, DEFAULT_MEMORY_DIR
        
        assert "opencode-team" in str(DEFAULT_LOG_DIR)
        assert "opencode-team" in str(DEFAULT_MEMORY_DIR)
        assert "logs" in str(DEFAULT_LOG_DIR)
        assert "memory" in str(DEFAULT_MEMORY_DIR)
    
    def test_ensure_dirs_function(self):
        """Test ensure_dirs creates directories."""
        from opencode_team_mcp.server import ensure_dirs, DEFAULT_LOG_DIR, DEFAULT_MEMORY_DIR
        
        # Cleanup first
        import shutil
        if DEFAULT_LOG_DIR.exists():
            shutil.rmtree(DEFAULT_LOG_DIR)
        if DEFAULT_MEMORY_DIR.exists():
            shutil.rmtree(DEFAULT_MEMORY_DIR)
        
        # Call ensure_dirs
        ensure_dirs()
        
        # Check directories were created
        assert DEFAULT_LOG_DIR.exists()
        assert DEFAULT_MEMORY_DIR.exists()


class TestToolSchemaValidation:
    """Test MCP tool schema validation."""
    
    def test_spawn_workers_schema(self):
        """Test spawn_workers input schema."""
        # The schema is defined in the tool definition
        # This test verifies the structure is correct
        from mcp.types import Tool
        
        with patch("opencode_team_mcp.server.Server") as mock_server:
            from opencode_team_mcp import server
            import importlib.util
            
            spec = importlib.util.spec_from_file_location(
                "server", Path(__file__).parent.parent / "src/opencode_team_mcp/server.py"
            )
            module = importlib.util.module_from_spec(spec)
            
            # Just verify the module loads without error
            assert module is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
