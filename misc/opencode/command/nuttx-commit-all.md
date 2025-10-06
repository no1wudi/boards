---
description: Generate NuttX commit message for all changes
agent: build
---

Generate a NuttX-style commit message for all current changes (both staged and unstaged).

First, let's check the current git status:
```bash
git status --porcelain
```

Now let's get all changes (both staged and unstaged):
```bash
git diff HEAD
```

**Rule: Read Entire Modified Files**
For each file that shows changes in the diff, you MUST read the entire file content to understand the full context of the changes. Use the file paths from the git status to read each complete file before generating the commit message. This provides a comprehensive view of the codebase and ensures accurate commit messages.

Based on the above changes, generate a commit message following the Apache NuttX RTOS format:

**Required Format:**
- First line: `<functional_area>: <short_self_explanatory_functional_context>`
- Blank line
- Description explaining what is changed, how, and why
- Can use several lines, short sentences, or bullet points
- End with signature (always use `git commit -s` to generate signoff info automatically, never hand write it)

**Example:**
```
net/can: Add g_ prefix to can_dlc_to_len and len_to_can_dlc

Add g_ prefix to can_dlc_to_len and len_to_can_dlc to
follow NuttX coding style conventions for global symbols,
improving code readability and maintainability.
* you can also use bullet points.
* to note different things briefly.

Signed-off-by: AuthorName <Valid@EmailAddress>
```

Please analyze all the changes and generate an appropriate NuttX-style commit message. Focus on:
1. The functional area affected (drivers/, sched/, net/, fs/, etc.)
2. What specifically changed
3. Why the change was necessary
4. How the change was implemented

The commit message should be clear, concise, and follow the NuttX coding standards.