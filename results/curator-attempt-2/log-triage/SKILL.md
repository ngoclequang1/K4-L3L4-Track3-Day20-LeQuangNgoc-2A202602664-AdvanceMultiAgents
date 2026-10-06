---
name: log-triage
description: Use this skill when processing log files to extract and structure error information according to conventions.
---
1. Filter log entries to include only those with ERROR or CRITICAL levels.
2. Convert timestamps to UTC format (YYYY-MM-DDTHH:MM:SSZ) for consistency.
3. Extract relevant fields: service name (in lower case with '-' replaced by '_'), error level, message, and exception details.
4. Count occurrences of each error message, including repeated messages indicated in the log.
5. Aggregate error counts by service for summary statistics.
6. Structure the output in a JSON format, ensuring it includes a top-level object with "schema_version" and "generated_by" fields.
7. Write the structured error data to `workspace/errors.json` following the specified schema.
