---
name: code-repair
description: Use when repairing a code package against docstrings, tests, and repository-specific review rules.
---
- Inspect the package, documentation, existing tests, and repository guidance before editing.
- Treat docstrings and specifications as behavioral contracts; cover every documented input format and edge case.
- Make the smallest targeted changes; preserve required behavior such as ordering and formatting.
- Do not modify original files in `tests/`; add new tests where permitted.
- Add `tests/test_regressions.py` with one test per fixed bug, at least three tests, and verify that file passes.
- Add type annotations to every parameter and return value of every public package function.
- Record each fix under `## Unreleased` in `CHANGELOG.md` as `- fix(<function name>): <short description>`.
- Run tests from the correct project root with the package import path configured; confirm collection succeeds before trusting results.
- Rerun the relevant suite after the final edit and report only verified outcomes.
