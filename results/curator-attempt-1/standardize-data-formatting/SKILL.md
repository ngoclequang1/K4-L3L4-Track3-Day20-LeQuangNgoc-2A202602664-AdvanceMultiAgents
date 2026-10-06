---
name: standardize-data-formatting
description: Use this skill to ensure consistent formatting of data values across different representations.
---
- Ensure all monetary values are represented in integer cents in the output JSON.
- Standardize date formats to ISO 8601 (YYYY-MM-DDTHH:MM:SSZ) for all timestamps.
- Capitalize and strip whitespace from region names to ensure consistency (e.g., "North", "South").
- Replace any special characters in service names with underscores (e.g., "payment-service" to "payment_service").
- Validate that all data entries conform to the specified formats before final output.
