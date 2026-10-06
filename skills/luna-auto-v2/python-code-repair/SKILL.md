---
name: python-code-repair
description: Use when repairing Python packages against existing tests, docstrings, or repository review rules.
---
- Inspect the package, docstrings, tests, and repository instructions before editing; treat docstrings and specified behavior as requirements.
- Do not modify existing files in `tests/`; add new tests in separate files.
- Add `tests/test_regressions.py` with at least three test functions, one for each fixed bug, and ensure it passes.
- Add type annotations for every parameter and return value of every public package function.
- Record every fix in `CHANGELOG.md` under `## Unreleased`, using bullets exactly formatted `- fix(<function name>): <short description>`; include at least three bullets.
- Make the smallest targeted changes; preserve unrelated behavior and ordering.
- Test boundary and alternate input formats from the specification, not just the failing example.
- Run the repository's tests from the correct project root and set the import path appropriately if needed; do not mistake collection or import errors for passing tests.
- Rerun the complete test suite after the final edit and report only verified results.
