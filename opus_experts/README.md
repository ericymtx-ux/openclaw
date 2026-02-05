# Opus Experts Knowledge Base

This folder contains knowledge and experience from Opus model sessions. It's designed to help improve the quality of responses from other models (like Minimax) by sharing successful task approaches.

---

## For Minimax Model

When you're working on a task, **search this folder first** to see if Opus has handled similar tasks before:

```bash
# Search for relevant experience
grep -r "keyword" /path/to/opus_experts/
# Or read all files and look for patterns
ls -la /path/to/opus_experts/*.md
```

**What to look for:**
- Similar command patterns
- Same tools used
- Same type of problem
- Files with titles containing relevant keywords

**How to apply:**
1. Read the `.md` files in this folder
2. Note the approach Opus took (commands, tools, order of operations)
3. Adapt the pattern to your current task
4. Follow the same quality standards

---

## For Opus Model

When you complete a **complex task successfully**, add a new `.md` file here:

**File naming:** `Task-Summary_YYYY-MM-DD.md`

**Include:**
- **Original instruction** - What the user asked for
- **Thought process** - Your reasoning and decision-making
- **Action steps** - Exact commands, tools, and workflow
- **Outcome** - What worked, what didn't, final result

**Example template:**

```markdown
# Task: Install ClawdHub Skills on macOS

**Date:** 2026-01-31

## Original Instruction
User asked me to find and install skills from ClawdHub that would help with AI agent development.

## Thought Process
1. First needed to understand the clawdhub CLI
2. Found the CLI had a missing dependency (undici)
3. Had to fix the dependency before searching
4. Used web fetch to explore the API when CLI search failed
5. Identified 4 relevant skills for development work
6. Installed them one by one

## Actions Taken
1. read /Users/apple/.npm-global/lib/node_modules/openclaw/skills/clawdhub/SKILL.md
2. clawdhub search "claude code" (failed)
3. clawdhub search coding (failed)
4. curl -sL "https://www.clawhub.ai/api/v1/skills" to fetch skill list
5. Analyzed results, selected: turix-cua, vibes, auto-updater, aifs-space
6. clawdhub install turix-cua --no-input
7. clawdhub install vibes --no-input
8. clawdhub install auto-updater --no-input
9. clawdhub install aifs-space --no-input
10. clawdhub list to verify

## Outcome
✅ All 4 skills installed successfully to /Users/apple/clawd/skills/
```

**Guidelines:**
- Be specific about commands and paths
- Include error handling if something went wrong
- Keep the title short but descriptive
- Add the date in filename for easy sorting
- Write in English for consistency

---

## File Structure

```
opus_experts/
├── README.md                    (this file)
└── Task-Summary_YYYY-MM-DD.md   (one file per complex task)
```

---

*This knowledge base grows with every successful Opus session. Use it wisely.*
