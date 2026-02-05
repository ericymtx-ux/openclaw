---
summary: "Guide for contributing to OpenClaw: setting up development environment, coding standards, and submission process"
read_when:
  - Setting up development environment
  - Following coding standards
  - Submitting contributions
title: "Contributing"
---

# Contributing to OpenClaw

Thank you for your interest in contributing to OpenClaw! This guide covers how to set up your development environment, follow our coding standards, and submit contributions.

## Getting Started

### Prerequisites

- Node.js 22+ (we recommend using [nvm](https://github.com/nvm-sh/nvm) to manage Node versions)
- pnpm (install via `npm install -g pnpm` or `brew install pnpm`)
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR-USERNAME/openclaw.git
cd openclaw
```

3. Add the upstream remote:

```bash
git remote add upstream https://github.com/openclaw/openclaw.git
```

### Setting Up Development Environment

1. Install dependencies:

```bash
pnpm install
```

2. Install pre-commit hooks:

```bash
pnpm prek install
```

3. Verify your setup:

```bash
pnpm lint
pnpm build
pnpm test
```

## Development Workflow

### Branch Naming

Follow these conventions:

- `feature/` for new features (e.g., `feature/new-channel`)
- `fix/` for bug fixes (e.g., `fix/memory-leak`)
- `docs/` for documentation changes
- `refactor/` for code refactoring

### Making Changes

1. Create a new branch from `main`:

```bash
git switch main
git pull upstream main
git checkout -b feature/your-feature
```

2. Make your changes following our coding standards
3. Run tests and linting:

```bash
pnpm lint
pnpm build
pnpm test
```

4. Commit your changes:

```bash
# Use the provided committer script
./scripts/committer "type: brief description of changes" file1.ts file2.ts
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (formatting, etc.)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

Example:

```
feat(channels): add WhatsApp message reactions support

Implement reaction sending and receiving for WhatsApp channel.

Closes #123
```

## Coding Standards

### TypeScript

- Use strict TypeScript (`"strict": true` in `tsconfig.json`)
- Avoid `any`; use `unknown` when type is uncertain
- Prefer interfaces over type aliases for object shapes
- Use descriptive variable and function names

```typescript
// Good
interface UserSession {
  id: string
  createdAt: Date
  lastActivity: Date
}

// Avoid
interface User {
  id: any
  data: any
}
```

### Code Formatting

We use Oxfmt for formatting:

```bash
pnpm format
```

### Linting

We use Oxlint:

```bash
pnpm lint
```

### File Organization

- Keep files under ~700 LOC when feasible
- Group related functionality in directories
- Place tests alongside source files:

```
src/
├── commands/
│   ├── send.ts
│   └── send.test.ts
```

### Comments

Add comments for complex logic:

```typescript
// Calculate exponential backoff with jitter
function calculateDelay(attempt: number): number {
  const baseDelay = Math.pow(2, attempt) * 1000
  const jitter = Math.random() * baseDelay * 0.1
  return Math.min(baseDelay + jitter, MAX_DELAY)
}
```

### Error Handling

Use structured errors:

```typescript
import { OpenClawError } from './errors'

function validateInput(input: unknown): asserts input is string {
  if (typeof input !== 'string') {
    throw new OpenClawError({
      code: 'INVALID_INPUT',
      message: 'Expected a string input',
      details: { input }
    })
  }
}
```

## Testing

### Running Tests

```bash
# All tests
pnpm test

# Unit tests
pnpm test

# Integration tests
pnpm test:e2e

# Live tests (requires API keys)
pnpm test:live
```

### Coverage Requirements

- Statements: 70%
- Branches: 70%
- Functions: 70%
- Lines: 70%

### Writing Tests

Follow the existing test patterns:

```typescript
import { describe, it, expect } from 'vitest'
import { yourFunction } from './your-file'

describe('your-file', () => {
  it('should handle expected input', () => {
    const result = yourFunction('input')
    expect(result).toBe('expected output')
  })

  it('should throw on invalid input', () => {
    expect(() => yourFunction('invalid')).toThrow()
  })
})
```

## Submitting Changes

### Pull Request Process

1. Push your branch to your fork:

```bash
git push origin feature/your-feature
```

2. Open a Pull Request against `main` on GitHub
3. Ensure all CI checks pass
4. Request review from maintainers

### PR Description Template

```markdown
## Summary
Brief description of changes

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated (if needed)
- [ ] Breaking changes documented (if any)
```

### Code Review Guidelines

- Be responsive to feedback
- Ask for clarification if needed
- Keep PRs focused and small
- Squash commits before merging (if requested)

## Documentation

### Updating Docs

1. Place documentation in `docs/`
2. Use Markdown format
3. Follow existing doc structure

### Doc Front Matter

```markdown
---
summary: "Brief summary of the page"
read_when:
  - When to read this doc
  - Another condition
title: "Page Title"
---
```

## Release Process

### Version Bumping

Use semantic versioning:

- `major`: Breaking changes
- `minor`: New features (backward compatible)
- `patch`: Bug fixes

### Changelog

Update `CHANGELOG.md` with:

- Description of changes
- PR number
- Contributor credits

## Getting Help

### Resources

- [Documentation](https://docs.openclaw.ai)
- [GitHub Issues](https://github.com/openclaw/openclaw/issues)
- [Discord Community](https://discord.gg/openclaw)

### Reporting Issues

When reporting bugs:

1. Check existing issues first
2. Include steps to reproduce
3. Share relevant logs
4. Provide environment details:

```bash
openclaw doctor
```
