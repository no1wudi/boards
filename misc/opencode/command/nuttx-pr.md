---
description: Generate NuttX-style PR description
agent: build
---

Generate a NuttX-style Pull Request description based on the last commit.

First, analyze the last commit:
```bash
git log -1 --pretty=format:"%H%n%s%n%b"
```

Get the changes from the last commit:
```bash
git show --name-only HEAD
```

Get the diff of the last commit:
```bash
git show HEAD
```

Based on the last commit's content and message, generate a comprehensive PR description following the Apache NuttX RTOS format:

**Required PR Description Format:**

```markdown
## Summary

  * Why change is necessary (fix, update, new feature)?
  * What functional part of the code is being changed?
  * How does the change exactly work (what will change and how)?
  * Related [NuttX Issue](https://github.com/apache/nuttx/issues) reference if applicable.
  * Related NuttX Apps [Issue](https://github.com/apache/nuttx-apps/issues) / [Pull Request](https://github.com/apache/nuttx-apps/pulls) reference if applicable.

## Impact

  * Is new feature added? Is existing feature changed? NO / YES (please describe if yes).
  * Impact on user (will user need to adapt to change)? NO / YES (please describe if yes).
  * Impact on build (will build process change)? NO / YES (please describe if yes).
  * Impact on hardware (will arch(s) / board(s) / driver(s) change)? NO / YES (please describe if yes).
  * Impact on documentation (is update required / provided)? NO / YES (please describe if yes).
  * Impact on security (any sort of implications)? NO / YES (please describe if yes).
  * Impact on compatibility (backward/forward/interoperability)? NO / YES (please describe if yes).
  * Anything else to consider or add?

## Testing

  I confirm that changes are verified on local setup and works as intended:
  * Build Host(s): OS (Linux,BSD,macOS,Windows,..), CPU(Intel,AMD,ARM), compiler(GCC,CLANG,version), etc.
  * Target(s): arch(sim,RISC-V,ARM,..), board:config, etc.
  * you can also provide steps on how to reproduce the problem and verify the change.

  Testing logs before change:

  ```
  build and runtime logs before change goes here
  ```

  Testing logs after change:

  ```
  build and runtime logs after change goes here
  ```

## PR verification Self-Check

  * [ ] This PR introduces only one functional change.
  * [ ] I have updated all required description fields above.
  * [ ] My PR adheres to Contributing [Guidelines](https://github.com/apache/nuttx/blob/master/CONTRIBUTING.md) and [Documentation](https://nuttx.apache.org/docs/latest/contributing/index.html) (git commit title and message, coding standard, etc).
  * [ ] My PR is still work in progress (not ready for review).
  * [ ] My PR is ready for review and can be safely merged into a codebase.
```

**Key Requirements:**
1. **Summary Section**: Must contain detailed explanation of purpose, necessity, and implementation
2. **Impact Section**: Must assess all impact areas (features, users, build, hardware, documentation, security, compatibility)
3. **Testing Section**: Must include build host details, target details, and before/after logs
4. **Self-Check**: Must verify adherence to NuttX guidelines

**Important Notes:**
- All fields are mandatory or the PR will be auto-rejected
- For code changes, build and runtime logs are mandatory for at least one real hardware target
- PR should be focused on only one functional change
- If this is a breaking change, it must be marked with `[BREAKING]` tag
- If this is experimental, it must be marked with `[EXPERIMENTAL]` tag
- Documentation updates must be included where applicable

Please analyze the last commit and generate a complete PR description following this format. Extract information from the commit message and changes to fill in the Summary, Impact, and Testing sections. Focus on providing comprehensive information that will help reviewers understand the change, its impact, and verify its correctness.