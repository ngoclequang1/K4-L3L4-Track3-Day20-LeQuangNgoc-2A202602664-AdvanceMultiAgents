---
name: code-repair
description: Use this skill when modifying code to ensure compliance with organizational rules and maintain test integrity.
---
1. Ensure that original test files in the `tests/` directory are not modified; create new test files as needed.
2. Verify that all public functions have type annotations for parameters and return values.
3. Implement changes to functions based on their docstring specifications, ensuring correct handling of edge cases.
4. Add regression tests for each bug fixed, creating a new test function for each in `tests/test_regressions.py`.
5. Update `CHANGELOG.md` with a bullet point for each fix under the heading '## Unreleased'.
6. Run the test suite to confirm all tests pass after modifications.
