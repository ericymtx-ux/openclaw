"""Pytest configuration and fixtures for opencode-team tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def mock_workers():
    """Create mock workers dictionary."""
    return {}


@pytest.fixture
def sample_worker():
    """Create a sample worker dictionary."""
    import uuid
    from datetime import datetime
    
    return {
        "session_id": str(uuid.uuid4())[:8],
        "name": "Groucho",
        "project_path": "/test/project",
        "prompt": "Test prompt",
        "annotation": "Test annotation",
        "status": "ready",
        "use_worktree": True,
        "skip_permissions": False,
        "started_at": datetime.utcnow().isoformat(),
        "last_activity": datetime.utcnow().isoformat(),
        "iterm": None
    }


@pytest.fixture
def mock_iterm_connection():
    """Create mock iTerm2 connection."""
    mock_conn = MagicMock()
    mock_app = MagicMock()
    mock_window = MagicMock()
    mock_tab = MagicMock()
    mock_session = MagicMock()
    
    mock_session.session_id = "test-session-123"
    mock_tab.sessions = [mock_session]
    mock_window.tabs = [mock_tab]
    mock_app.terminal_windows = [mock_window]
    
    mock_conn.async_get_app = MagicMock(return_value=mock_app)
    
    return mock_conn, mock_app, mock_window, mock_tab, mock_session


@pytest.fixture
def mock_mcp_request():
    """Create mock MCP request context."""
    return MagicMock()
