---
summary: "Integration testing guide for OpenClaw: running integration tests, writing new tests, and CI integration"
read_when:
  - Running integration tests locally
  - Adding new integration tests
  - Setting up CI for integration tests
title: "Integration Tests"
---

# Integration Tests

OpenClaw's integration test suite validates the interaction between components, including gateway networking, agent tool calls, and multi-step workflows.

## Running Integration Tests

### Basic Commands

```bash
# Run all integration tests
pnpm test:e2e

# Run a specific test file
pnpm test:e2e src/gateway/gateway.tool-calling.mock-openai.test.ts

# Run with coverage
pnpm test:e2e --coverage
```

### Configuration

Integration tests use `vitest.e2e.config.ts`:

```typescript
// vitest.e2e.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    include: ['src/**/*.e2e.test.ts'],
    pool: 'threads',
    poolOptions: {
      threads: {
        maxThreads: 8,
        minThreads: 2
      }
    },
    testTimeout: 30000
  }
})
```

## Test Categories

### Gateway Tests

Validate gateway behavior including:

- WebSocket connections and authentication
- HTTP API endpoints
- Session management
- Channel routing

```typescript
// Example: gateway session test
describe('gateway session', () => {
  it('should create and manage sessions correctly', async () => {
    const gateway = await createTestGateway()
    const session = await gateway.createSession()
    expect(session.id).toBeDefined()
    await gateway.closeSession(session.id)
  })
})
```

### Tool Calling Tests

Verify tool invocation through the agent pipeline:

- Direct tool calls
- Multi-turn tool conversations
- Tool error handling

```typescript
// Example: tool calling test
describe('tool calling', () => {
  it('should execute read tool correctly', async () => {
    const result = await testAgent.run('read /test/file.txt')
    expect(result.tool).toBe('read')
    expect(result.content).toContain('expected content')
  })
})
```

### Channel Integration Tests

Test message flow through channels:

- Message sending and receiving
- Reaction handling
- Media processing

## Writing Integration Tests

### Test Structure

Follow the existing test patterns:

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { createTestGateway } from './fixtures/gateway'

describe('feature area', () => {
  let gateway: TestGateway

  beforeAll(async () => {
    gateway = await createTestGateway()
  })

  afterAll(async () => {
    await gateway.close()
  })

  it('should handle expected behavior', async () => {
    const result = await gateway.sendMessage('test message')
    expect(result.success).toBe(true)
  })
})
```

### Using Mocks

Mock external services for deterministic tests:

```typescript
import { mockProvider } from './mocks/provider'

describe('with mock provider', () => {
  it('should handle provider response', async () => {
    mockProvider.setResponse({
      content: 'mocked response',
      tool_calls: []
    })
    const result = await agent.run('test prompt')
    expect(result.content).toBe('mocked response')
  })
})
```

### Test Fixtures

Reusable test setup in `src/test/fixtures/`:

```typescript
// src/test/fixtures/gateway.ts
export async function createTestGateway(options?: GatewayOptions) {
  const gateway = new TestGateway({
    ...defaultOptions,
    ...options
  })
  await gateway.start()
  return gateway
}
```

## CI Integration

### GitHub Actions Workflow

```yaml
name: Integration Tests

on:
  push:
    branches: [main]
  pull_request:

jobs:
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: pnpm
      - run: pnpm install
      - run: pnpm build
      - run: pnpm test:e2e
```

### Running in Docker

```bash
# Build the test image
docker build -t openclaw-test -f Dockerfile.test .

# Run integration tests
docker run --rm openclaw-test pnpm test:e2e
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Timeout errors | Increase `testTimeout` or check for hanging operations |
| Flaky tests | Check for race conditions; use proper async cleanup |
| Mock failures | Verify mock setup and response format |

### Debug Mode

Run tests with verbose output:

```bash
pnpm test:e2e --reporter=verbose
```
