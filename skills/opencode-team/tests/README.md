# OpenCode Team MCP Server Tests

This directory contains unit tests for the OpenCode Team MCP server.

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/opencode_team_mcp --cov-report=term-missing

# Run specific test class
pytest tests/test_server.py::TestSpawnWorkers -v

# Run specific test
pytest tests/test_server.py::TestSpawnWorkers::test_spawn_single_worker -v
```

## Test Structure

| Test Class | Tests | Description |
|------------|-------|-------------|
| `TestWorkerNameGeneration` | 3 | Worker name generation and wrapping |
| `TestWorkerState` | 1 | Worker dictionary structure validation |
| `TestDirectorySetup` | 2 | Default log and memory directory paths |
| `TestWorkerNames` | 3 | Worker name list contains expected names |
| `TestMCPResponseFormatting` | 2 | Response formatting for workers list |
| `TestSessionIDGeneration` | 2 | Session ID format and uniqueness |
| `TestCommandConstruction` | 3 | Command string construction |
| `TestSpawnWorkers` | 8 | spawn_workers MCP tool |
| `TestListWorkers` | 5 | list_workers MCP tool |
| `TestMessageWorkers` | 5 | message_workers MCP tool |
| `TestCheckIdleWorkers` | 5 | check_idle_workers MCP tool |
| `TestCloseWorkers` | 5 | close_workers MCP tool |

**Total: 44 tests**

## MCP Tool Coverage

### spawn_workers
- Single worker spawning
- Multiple workers spawning
- Auto project path (uses env var)
- iTerm2 window info creation
- Default annotation (50 char truncation)
- Ready status on spawn
- Worktree enabled by default
- Skip permissions option

### list_workers
- List all workers
- Filter by status (ready, busy, closed)
- Empty result handling

### message_workers
- Send message to single worker
- Set worker to busy status
- Multiple workers
- Nonexistent worker handling
- Empty session IDs

### check_idle_workers
- Find ready/idle workers
- Exclude busy workers
- Correct count reporting
- Empty session IDs
- All workers busy scenario

### close_workers
- Close single worker
- Close multiple workers
- Nonexistent worker handling
- Already closed worker
- Empty list

## Fixtures

- `fresh_server_state`: Resets workers dict and counter before each test
- `server_with_workers`: Pre-populates workers with test data
- Mock fixtures: `mock_iterm_connection`, `mock_mcp_request`

## Mocking Strategy

Tests use `unittest.mock.patch` to:
- Mock iTerm2 window creation
- Mock state persistence (`save_worker_state`)
- Test tool logic without iTerm2 dependencies
