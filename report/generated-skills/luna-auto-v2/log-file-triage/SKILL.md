---
name: log-file-triage
description: Use when parsing application logs into structured error records and service-level summaries.
---
- Read the complete task specification and log before parsing; identify entry boundaries, continuation lines, severity spellings, and repeat-marker placement.
- Follow the task's accepted error levels exactly; normalize service names to lowercase and replace `-` with `_`.
- Convert timezone-aware timestamps to UTC before formatting; never append `Z` to an unconverted local timestamp.
- Attach multiline exception details to their originating entry; use `null` only when no traceback or exception exists.
- Set `repeat_count` to 1 plus the sum of repeat-marker counts following that entry, including markers after its continuation lines.
- Compute `counts_by_service` as the sum of `repeat_count` per service over the specified entries.
- Sort `errors` by service, then by `timestamp_utc`, both ascending.
- Preserve the required top-level JSON schema exactly, including `"schema_version": 2` and `"generated_by": "log-triage"`.
- Verify entry totals, field values, repeat aggregation, ordering, and JSON validity before writing the final artifact.
- Give the requested concise parsing summary only after validating the output.
