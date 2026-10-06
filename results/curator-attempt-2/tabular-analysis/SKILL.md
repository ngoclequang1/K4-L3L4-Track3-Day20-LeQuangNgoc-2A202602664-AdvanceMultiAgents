---
name: tabular-analysis
description: Use this skill when analyzing tabular data to ensure proper formatting and compliance with output requirements.
---
1. Read the input CSV file and handle date formats consistently, converting all timestamps to UTC.
2. Standardize categorical data (e.g., region names) by stripping whitespace and capitalizing appropriately.
3. Replace any placeholder values (e.g., -999 for missing amounts) with `NaN` or appropriate representations.
4. Remove duplicate rows based on unique identifiers (e.g., order_id).
5. Calculate required metrics and ensure monetary values are represented in integer cents.
6. Write the cleaned data to `workspace/clean.csv` with the specified header and format.
7. Create an `answer.json` file containing the required metrics and ensure it follows the specified schema.
