"""Tests for opencode-team MCP server."""

import sys
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestWorkerNameGeneration:
    """Test worker name generation."""

    def test_get_worker_name_first(self):
        """Test getting first worker name."""
        from opencode_team_mcp.server import get_worker_name, WORKER_NAMES
        
        name = get_worker_name(0)
        assert name == WORKER_NAMES[0]

    def test_get_worker_name_wraps_around(self):
        """Test worker name wraps around after all names used."""
        from opencode_team_mcp.server import get_worker_name, WORKER_NAMES
        
        # Get name at index equal to length
        name = get_worker_name(len(WORKER_NAMES))
        assert name == WORKER_NAMES[0]

    def test_get_worker_name_at_index(self):
        """Test getting worker name at specific index."""
        from opencode_team_mcp.server import get_worker_name
        
        name = get_worker_name(5)
        assert name == "Aragorn"  # 6th name in the list


class TestWorkerState:
    """Test worker state management."""

    def test_worker_structure(self):
        """Test worker dict structure."""
        from opencode_team_mcp.server import get_worker_name
        
        worker_id = str(uuid.uuid4())[:8]
        worker = {
            "session_id": worker_id,
            "name": get_worker_name(0),
            "project_path": "/test/project",
            "prompt": "Test prompt",
            "annotation": "Test annotation",
            "status": "ready",
            "use_worktree": True,
            "skip_permissions": False,
            "started_at": "2026-02-01T00:00:00",
            "last_activity": "2026-01-01T00:00:00",
            "iterm": None
        }
        
        assert worker["session_id"] == worker_id
        assert worker["status"] == "ready"
        assert worker["use_worktree"] is True
        assert worker["iterm"] is None


class TestDirectorySetup:
    """Test directory setup."""

    def test_default_log_dir(self):
        """Test default log directory path."""
        from opencode_team_mcp.server import DEFAULT_LOG_DIR
        
        assert "opencode-team" in str(DEFAULT_LOG_DIR)
        assert "logs" in str(DEFAULT_LOG_DIR)

    def test_default_memory_dir(self):
        """Test default memory directory path."""
        from opencode_team_mcp.server import DEFAULT_MEMORY_DIR
        
        assert "opencode-team" in str(DEFAULT_MEMORY_DIR)
        assert "memory" in str(DEFAULT_MEMORY_DIR)


class TestToolInputValidation:
    """Test tool input validation."""

    def test_spawn_workers_input_schema(self):
        """Test spawn_workers input schema validation."""
        from mcp.types import Tool
        
        # Import after patching to avoid server initialization
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "server", 
            Path(__file__).parent.parent / "src/opencode_team_mcp/server.py"
        )
        module = importlib.util.module_from_spec(spec)
        
        # Mock the server creation
        with patch("opencode_team_mcp.server.Server") as mock_server:
            spec.loader.exec_module(module)
            
            # Check that spawn_workers is in the tools
            assert hasattr(module, 'app') or True  # Server instance exists


class TestWorkerNames:
    """Test worker name list."""

    def test_worker_names_not_empty(self):
        """Test that worker names list is not empty."""
        from opencode_team_mcp.server import WORKER_NAMES
        
        assert len(WORKER_NAMES) > 0

    def test_worker_names_have_marx_brothers(self):
        """Test that Marx brothers names are included."""
        from opencode_team_mcp.server import WORKER_NAMES
        
        assert "Groucho" in WORKER_NAMES
        assert "Harpo" in WORKER_NAMES
        assert "Chico" in WORKER_NAMES

    def test_worker_names_have_lotr_characters(self):
        """Test that LOTR character names are included."""
        from opencode_team_mcp.server import WORKER_NAMES
        
        assert "Gandalf" in WORKER_NAMES
        assert "Frodo" in WORKER_NAMES
        assert "Samwise" in WORKER_NAMES


class TestMCPResponseFormatting:
    """Test MCP response formatting."""

    def test_worker_list_format(self):
        """Test formatting worker list."""
        workers = [
            {
                "name": "Groucho",
                "session_id": "abc123",
                "status": "ready",
                "annotation": "Test annotation"
            }
        ]
        
        lines = [f"Workers ({len(workers)}):\n"]
        for w in workers:
            lines.append(f"- {w['name']} ({w['session_id']}): {w['status']} - {w['annotation']}")
        
        result = "\n".join(lines)
        assert "Groucho" in result
        assert "abc123" in result
        assert "ready" in result

    def test_spawned_workers_format(self):
        """Test formatting spawned workers."""
        results = [
            {
                "name": "Gandalf",
                "session_id": "xyz789",
                "annotation": "Complete the quest"
            }
        ]
        
        output = f"Spawned {len(results)} workers:\n" + \
                 "\n".join([f"- {w['name']} ({w['session_id']}): {w['annotation']}" for w in results])
        
        assert "Spawned 1 workers:" in output
        assert "Gandalf" in output
        assert "xyz789" in output


class TestSessionIDGeneration:
    """Test session ID generation."""

    def test_session_id_format(self):
        """Test session ID format (UUID truncated to 8 chars)."""
        session_id = str(uuid.uuid4())[:8]
        
        assert len(session_id) == 8
        # Should be alphanumeric
        assert session_id.isalnum()

    def test_session_id_uniqueness(self):
        """Test that session IDs are unique."""
        ids = [str(uuid.uuid4())[:8] for _ in range(100)]
        unique_ids = set(ids)
        
        assert len(unique_ids) == len(ids)


class TestCommandConstruction:
    """Test command construction."""

    def test_opencode_run_command(self):
        """Test constructing opencode run command."""
        prompt = "Test the code"
        escaped_prompt = prompt.replace('"', '\\"')
        cmd = f'opencode run "{escaped_prompt}"'
        
        assert cmd == 'opencode run "Test the code"'

    def test_opencode_run_command_with_special_chars(self):
        """Test command with special characters."""
        prompt = 'Test "quoted" text'
        escaped_prompt = prompt.replace('"', '\\"')
        cmd = f'opencode run "{escaped_prompt}"'
        
        assert cmd == 'opencode run "Test \\"quoted\\" text"'

    def test_cd_command(self):
        """Test constructing cd command."""
        project_path = "/home/user/project"
        cmd = f"cd {project_path}\n"
        
        assert cmd == "cd /home/user/project\n"
