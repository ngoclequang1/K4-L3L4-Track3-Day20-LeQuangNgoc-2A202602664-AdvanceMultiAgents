---
name: tabular-analysis
description: Use when cleaning tabular inputs, computing requested metrics, or producing structured data outputs.
---
- Read the task specification and data dictionary before choosing parsers, identifiers, missing-value sentinels, date formats, or category normalization.
- Check available tools and libraries before relying on them; use standard-library alternatives when needed.
- Inspect input rows and types; validate parsing across all documented formats rather than assuming one format.
- Apply missing-value handling and deduplication using the specified sentinel and identifier; determine whether deduplication precedes each metric.
- Normalize categories to the specified canonical spellings.
- Convert timestamps to timezone-aware UTC before formatting; never append `Z` to a local or offset timestamp without converting it.
- Compute money in the required unit and representation, such as integer cents when specified.
- Verify metric values and row counts against the cleaned data, including duplicate and missing-value accounting.
- Preserve exact output paths, headers, column order, JSON keys, metadata fields, and required row-selection rules.
- Write only the requested artifacts and validate that they are parseable and conform to the specified schema.
