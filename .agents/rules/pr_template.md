---
description: Custom Pull Request Template Rule
---

When the user asks you to create a Pull Request (PR) or write a PR description, you MUST follow the template provided in `.github/pull_request_template.md`. 
If you can't read that file for any reason, use the following structure:

## Type
<!-- Pick one: Feature | Fix | Refactor | Style | Chore | Docs -->

## Summary
<!-- 1-3 sentences: what does this PR do and why -->

## Changes
-
-

## Related
<!-- Link an issue/task if one exists, or say "N/A" -->

## Testing
- [ ] Tested locally
- [ ] No new errors/warnings in console
- [ ] Existing functionality still works (manual check)

## What might break
<!-- 1-2 sentences: what's the riskiest part of this change, what should you watch for after merging -->

## Screenshots (if UI change)

## Checklist
- [ ] No secrets/API keys committed
- [ ] `.env.example` updated if new env vars were added
- [ ] Code follows existing project structure/conventions
- [ ] Self-reviewed the diff before requesting merge
