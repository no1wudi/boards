---
description: Generate NuttX commit message interactively
agent: build
---

Generate a NuttX-style commit message through an interactive process.

**Step 1: Analyze Current Changes**
First, check the current git status to see what files are modified:
```bash
git status --porcelain
```

**Step 2: Review Staged Changes**
Check what changes are currently staged:
```bash
git diff --cached
```

**Step 3: Review Unstaged Changes (if needed)**
If there are no staged changes, check unstaged changes:
```bash
git diff
```

**Step 4: Group Changes Logically**
Analyze all changes and group them logically following minimal commit principles. Consider:
- Are these changes related to the same functional area?
- Do they address the same issue or feature?
- Should they be committed together or separately?

**Step 5: Get User Confirmation**
Present a draft commit message and ask:
"Proposed commit message: [draft message]
Any modifications needed to this commit message, or should we proceed with this?"

**Step 6: Generate Commit Message**
Once the user confirms the grouping, generate a NuttX-style commit message following the Apache NuttX RTOS format:

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

Please analyze the changes and generate an appropriate NuttX-style commit message. Focus on:
1. The functional area affected (drivers/, sched/, net/, fs/, etc.)
2. What specifically changed
3. Why the change was necessary
4. How the change was implemented

The commit message should be clear, concise, and follow the NuttX coding standards.