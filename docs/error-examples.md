---
summary: "Common error patterns and handling examples for OpenClaw agents and gateways"
read_when:
  - Debugging errors in your agent
  - Understanding error responses
  - Implementing error handling
title: "Error Examples"
---

# Error Examples

This guide covers common error patterns in OpenClaw and how to handle them.

## Authentication Errors

### Missing API Key

```json
{
  "error": {
    "code": "AUTH_MISSING",
    "message": "API key not configured for provider 'openai'",
    "provider": "openai",
    "hint": "Run 'openclaw models auth' to configure credentials"
  }
}
```

**Resolution**: Configure credentials using the CLI:

```bash
openclaw models auth --provider openai
```

### Invalid API Key

```json
{
  "error": {
    "code": "AUTH_INVALID",
    "message": "API key is invalid or expired",
    "provider": "anthropic",
    "hint": "Update your API key with 'openclaw models auth --provider anthropic'"
  }
}
```

### Expired Token

```json
{
  "error": {
    "code": "AUTH_EXPIRED",
    "message": "Authentication token has expired",
    "provider": "google-antigravity",
    "hint": "Re-authenticate using the provider's OAuth flow"
  }
}
```

## Gateway Errors

### Gateway Unreachable

```json
{
  "error": {
    "code": "GATEWAY_UNREACHABLE",
    "message": "Cannot connect to OpenClaw gateway",
    "details": {
      "address": "127.0.0.1",
      "port": 18789
    },
    "hint": "Ensure the gateway is running: 'openclaw gateway start'"
  }
}
```

**Resolution**: Start the gateway:

```bash
openclaw gateway start
```

### Session Not Found

```json
{
  "error": {
    "code": "SESSION_NOT_FOUND",
    "message": "Session 'agent:dev:abc123' does not exist",
    "sessionId": "agent:dev:abc123",
    "hint": "Create a new session or use an existing session ID"
  }
}
```

### Session Stale

```json
{
  "error": {
    "code": "SESSION_STALE",
    "message": "Session has been inactive for too long",
    "sessionId": "agent:dev:abc123",
    "lastActivity": "2024-01-15T10:30:00Z",
    "hint": "Create a new session to continue"
  }
}
```

## Tool Errors

### Tool Not Found

```json
{
  "error": {
    "code": "TOOL_NOT_FOUND",
    "message": "Tool 'nonexistent_tool' is not available",
    "requested": "nonexistent_tool",
    "available": ["read", "write", "exec", "grep"]
  }
}
```

### Tool Execution Failed

```json
{
  "error": {
    "code": "TOOL_FAILED",
    "message": "Tool 'exec' failed with exit code 1",
    "tool": "exec",
    "command": "npm install",
    "exitCode": 1,
    "stderr": "npm ERR! Could not resolve dependencies"
  }
}
```

### Tool Timeout

```json
{
  "error": {
    "code": "TOOL_TIMEOUT",
    "message": "Tool 'exec' exceeded timeout",
    "tool": "exec",
    "command": "sleep 60",
    "timeoutMs": 30000,
    "hint": "Increase timeout or optimize the command"
  }
}
```

### Sandbox Restriction

```json
{
  "error": {
    "code": "SANDBOX_RESTRICTED",
    "message": "Command blocked by sandbox policy",
    "command": "rm -rf /",
    "policy": "deny-destructive"
  }
}
```

## Provider Errors

### Rate Limited

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded",
    "provider": "openai",
    "retryAfterMs": 5000,
    "limit": {
      "type": "requests",
      "limit": 100,
      "window": "1m"
    }
  }
}
```

**Resolution**: Implement exponential backoff:

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3
): Promise<T> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      if (error.code === 'RATE_LIMITED' && attempt < maxRetries) {
        const delay = error.retryAfterMs * attempt
        await sleep(delay)
        continue
      }
      throw error
    }
  }
  throw new Error('Max retries exceeded')
}
```

### Model Not Found

```json
{
  "error": {
    "code": "MODEL_NOT_FOUND",
    "message": "Model 'openai/gpt-99' is not available",
    "requested": "openai/gpt-99",
    "suggested": "openai/gpt-5.2"
  }
}
```

### Provider Unavailable

```json
{
  "error": {
    "code": "PROVIDER_UNAVAILABLE",
    "message": "Provider 'anthropic' is temporarily unavailable",
    "provider": "anthropic",
    "retryAfterMs": 30000
  }
}
```

## Channel Errors

### Message Send Failed

```json
{
  "error": {
    "code": "MESSAGE_SEND_FAILED",
    "message": "Failed to send message to Telegram",
    "channel": "telegram",
    "chatId": "123456789",
    "reason": "chat not found"
  }
}
```

### Webhook Verification Failed

```json
{
  "error": {
    "code": "WEBHOOK_VERIFY_FAILED",
    "message": "Webhook verification failed",
    "channel": "telegram",
    "reason": "invalid token"
  }
}
```

## Error Handling Best Practices

### Structured Error Handling

```typescript
import { OpenClawError } from '@openclaw/errors'

try {
  await agent.run('some command')
} catch (error) {
  if (error instanceof OpenClawError) {
    console.error(`Error ${error.code}: ${error.message}`)
    if (error.hint) {
      console.error(`Hint: ${error.hint}`)
    }
  } else {
    console.error('Unexpected error:', error)
  }
}
```

### Error Recovery Patterns

```typescript
// Pattern 1: Graceful degradation
async function withFallback(primary: () => Promise<T>, fallback: () => Promise<T>) {
  try {
    return await primary()
  } catch (error) {
    if (isRecoverable(error)) {
      return await fallback()
    }
    throw error
  }
}

// Pattern 2: Circuit breaker
const circuit = new CircuitBreaker({
  failureThreshold: 5,
  resetTimeout: 60000
})

circuit.on('open', () => {
  console.warn('Circuit breaker opened - using fallback')
})
```

### Logging Errors

```typescript
import { logger } from './logging'

function handleError(error: OpenClawError) {
  logger.error('Operation failed', {
    code: error.code,
    message: error.message,
    provider: error.provider,
    sessionId: error.sessionId
  })
}
```
