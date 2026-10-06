---
name: code-repair
description: Use this skill when modifying code to ensure compliance with organizational rules and maintain functionality.
---
1. Ensure that original test files in the `tests/` directory are not modified; create new test files as needed.
2. Verify that all public functions have type annotations for parameters and return values.
3. Update the `CHANGELOG.md` file under '## Unreleased' with a bullet for each fix, formatted as '- fix(<function name>): <short description>'.
4. Ensure that any changes to functions are accompanied by corresponding regression tests in `tests/test_regressions.py`.
5. When modifying price parsing functions, ensure they handle all specified formats, including accounting styles.
6. Confirm that any changes to sorting or filtering functions maintain the expected output format and order.
