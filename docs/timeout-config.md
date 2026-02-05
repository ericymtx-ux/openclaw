---
summary: "Comprehensive timeout configuration guide for OpenClaw agents, gateways, and tools"
read_when:
  - Configuring timeouts for different operations
  - Debugging timeout-related issues
  - Optimizing performance with timeout tuning
title: "Timeout Configuration"
---

# Timeout Configuration

OpenClaw provides granular timeout controls for agents, gateways, and tools. This guide covers all available timeout settings and their recommended values.

## Agent Timeouts

### Default Configuration

```json
{
  "agent": {
    "defaultTimeout": 300000,
    "maxTimeout": 600000,
    "thinkingTimeout": 30000,
    "toolTimeout": 60000
  }
}
```

### Timeout Properties

| Property | Description | Default | Unit |
|----------|-------------|---------|------|
| `defaultTimeout` | Default agent run timeout | 300000 | ms |
| `maxTimeout` | Maximum allowed timeout | 600000 | ms |
| `thinkingTimeout` | Model thinking time | 30000 | ms |
| `toolTimeout` | Individual tool execution | 60000 | ms |

### Per-Model Timeout Overrides

```json
{
  "models": {
    "anthropic/claude-opus-4-5": {
      "timeout": 300000
    },
    "openai/gpt-5.2": {
      "timeout": 180000
    }
  }
}
```

## Gateway Timeouts

### WebSocket Timeouts

```json
{
  "gateway": {
    "websocket": {
      "connectionTimeout": 10000,
      "idleTimeout": 300000,
      "pingInterval": 30000
    },
    "http": {
      "requestTimeout": 30000,
      "idleTimeout": 120000
    }
  }
}
```

### Session Timeouts

```json
{
  "session": {
    "idleTimeout": 3600000,
    "maxLifetime": 86400000,
    "staleAfter": 1800000
  }
}
```

## Tool Timeouts

### Per-Tool Configuration

```json
{
  "tools": {
    "read": {
      "timeout": 10000
    },
    "write": {
      "timeout": 30000
    },
    "exec": {
      "timeout": 120000
    },
    "grep": {
      "timeout": 60000
    }
  }
}
```

### Default Tool Timeout

```json
{
  "tools": {
    "defaultTimeout": 60000,
    "maxTimeout": 300000
  }
}
```

## Channel Timeouts

### Per-Channel Configuration

```json
{
  "channels": {
    "telegram": {
      "messageTimeout": 30000,
      "webhookTimeout": 10000
    },
    "discord": {
      "messageTimeout": 30000,
      "webhookTimeout": 10000
    },
    "whatsapp": {
      "messageTimeout": 45000,
      "webhookTimeout": 15000
    }
  }
}
```

## Provider Timeouts

### API Request Timeouts

```json
{
  "providers": {
    "openai": {
      "timeout": 60000,
      "connectTimeout": 10000
    },
    "anthropic": {
      "timeout": 60000,
      "connectTimeout": 10000
    },
    "google": {
      "timeout": 60000,
      "connectTimeout": 10000
    }
  }
}
```

### Retry Configuration

```json
{
  "providers": {
    "openai": {
      "retry": {
        "maxAttempts": 3,
        "initialDelay": 1000,
        "maxDelay": 30000,
        "backoffMultiplier": 2
      }
    }
  }
}
```

## Environment Variables

### Override Timeouts via Environment

```bash
# Agent timeout (5 minutes)
export OPENCLAW_AGENT_TIMEOUT=300000

# Tool execution timeout
export OPENCLAW_TOOL_TIMEOUT=60000

# Gateway WebSocket timeout
export OPENCLAW_GATEWAY_WS_TIMEOUT=300000

# Provider request timeout
export OPENCLAW_PROVIDER_TIMEOUT=60000
```

### Priority Order

1. Environment variable (highest priority)
2. Per-model configuration
3. Per-tool configuration
4. Default configuration (lowest priority)

## Timeout Recommendations

### Development

```json
{
  "agent": {
    "defaultTimeout": 600000
  },
  "tools": {
    "defaultTimeout": 120000
  }
}
```

### Production

```json
{
  "agent": {
    "defaultTimeout": 180000
  },
  "tools": {
    "defaultTimeout": 30000
  }
}
```

### High-Latency Operations

For operations like file scanning or large model responses:

```json
{
  "agent": {
    "defaultTimeout": 600000
  },
  "tools": {
    "grep": {
      "timeout": 120000
    },
    "exec": {
      "timeout": 180000
    }
  }
}
```

## Monitoring and Debugging

### Timeout Metrics

Enable timeout tracking in diagnostics:

```json
{
  "diagnostics": {
    "enabled": true,
    "flags": ["timeout"]
  }
}
```

### Log Timeout Events

```bash
# Tail timeout-related logs
openclaw logs --follow | grep -i timeout
```

### Common Timeout Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Agent timeout | Complex task | Increase timeout or break into smaller tasks |
| Tool timeout | Long-running command | Optimize command or increase tool timeout |
| Provider timeout | Network issues | Check connectivity, increase timeout |
| WebSocket timeout | Idle connection | Increase idle timeout or enable ping |

## Best Practices

1. **Set reasonable defaults**: Start with conservative timeouts and adjust based on observed behavior
2. **Monitor and iterate**: Use diagnostics to identify timeout patterns
3. **Use per-operation overrides**: Configure longer timeouts for known slow operations
4. **Implement retries**: Use exponential backoff for transient failures
5. **Log timeout events**: Track timeouts to identify optimization opportunities
