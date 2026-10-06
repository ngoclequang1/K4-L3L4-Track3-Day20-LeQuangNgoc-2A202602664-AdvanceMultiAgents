---
name: log-triage
description: Use when parsing application logs into structured error records and service-level summaries.
---
- Read the log format and output conventions before parsing; identify entry boundaries, continuation lines, and repeat markers.
- Select only the specified severity levels and preserve the required field semantics.
- Convert each timestamp to timezone-aware UTC before formatting it as `YYYY-MM-DDTHH:MM:SSZ`.
- Associate stack traces and exception details with their originating entry; represent missing exception data exactly as specified.
- Add each repeat marker's stated count to its preceding entry, following the specified handling of continuation lines.
- Normalize service names to lowercase and replace hyphens with underscores when required.
- Sort errors by normalized service, then by UTC timestamp, ascending.
- Compute service counts as the sum of each included entry's `repeat_count`.
- Preserve the exact top-level schema, including `"schema_version": 2` and `"generated_by": "log-triage"`, and validate the completed output.
=== END===
