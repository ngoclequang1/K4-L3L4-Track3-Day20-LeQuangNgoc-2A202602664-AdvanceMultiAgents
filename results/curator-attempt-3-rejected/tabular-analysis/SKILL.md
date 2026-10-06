---
name: tabular-analysis
description: Use this skill when analyzing and cleaning tabular data to ensure accuracy and compliance with output specifications.
---
1. Read the input CSV file and handle date formats consistently, converting all timestamps to UTC.
2. Standardize categorical fields by stripping whitespace and capitalizing entries according to canonical spelling.
3. Replace sentinel values (e.g., -999) with appropriate missing value indicators (e.g., `NaN`).
4. Remove duplicate rows based on unique identifiers, ensuring only distinct entries are retained.
5. Calculate required metrics accurately, ensuring that monetary values are represented in integer cents.
6. Write the cleaned data to `workspace/clean.csv` with the specified header and format.
