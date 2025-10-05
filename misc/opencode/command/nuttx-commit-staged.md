---
description: Generate NuttX commit message for staged changes
agent: build
---

Generate a NuttX-style commit message for staged changes.

Current staged changes:
```bash
git diff --cached
```

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

Please analyze the staged changes and generate an appropriate NuttX-style commit message. Focus on:
1. The functional area affected (drivers/, sched/, net/, fs/, etc.)
2. What specifically changed
3. Why the change was necessary
4. How the change was implemented

The commit message should be clear, concise, and follow the NuttX coding standards.