---
name: log-triage
description: Use this skill when processing log files to extract and structure error information according to specified conventions.
---
1. Filter log entries to include only those with ERROR or CRITICAL levels.
2. Convert timestamps to UTC format (YYYY-MM-DDTHH:MM:SSZ) for consistency.
3. Extract relevant fields: service name (in lower case with '-' replaced by '_'), error level, message, and exception details.
4. Count occurrences of each error message, including repetitions indicated by log entries.
5. Aggregate error counts by service for summary reporting.
6. Structure the output in `workspace/errors.json` with the required schema, including `schema_version` and `generated_by` fields.
