---
description: Check active New Relic alert violations
---

# New Relic Alerts Check

Check for active alert violations in New Relic.

## Instructions

1. Verify environment variables:
```bash
test -n "$NEW_RELIC_API_KEY" && echo "OK" || echo "MISSING: set NEW_RELIC_API_KEY"
```

2. Fetch open violations:
```bash
curl -s -X GET 'https://api.newrelic.com/v2/alerts_violations.json?only_open=true' \
  -H "Api-Key: $NEW_RELIC_API_KEY" \
  | python3 -m json.tool
```

3. Present results as a summary:
   - Count of active violations
   - Each violation: entity name, condition name, severity, opened at
   - If no violations, report "No active alert violations"
