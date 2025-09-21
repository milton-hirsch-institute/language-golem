---
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git branch:*), Bash(git log:*)
description: Print a commit message for current change
---

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

# Your task

Print a concise commit message for the current staged and unstaged changes using the commit message style from ../pipeline-agent/STYLE.md.

Follow this process:
1. Analyze the changes to categorize them (Changes, Features, Fixes, Tests, Refactoring)
1. Create a commit message following this structure:
   - Clear, concise subject line (50 characters or less)
   - Blank line
   - Organized sections with bullet points (only include relevant sections)
   - Do not end with generation attribution

Only include sections that are relevant to the changes. Focus on what was changed, not why.

Example structure:
```
Subject line describing the main change

Changes:
- List specific modifications made
- Focus on what was changed

Features:
- New functionality added (if applicable)

Fixes:
- Bug fixes and corrections (if applicable)

Tests:
- New test cases added (if applicable)
```
