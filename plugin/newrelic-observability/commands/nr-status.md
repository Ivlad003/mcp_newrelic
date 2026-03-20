---
description: Get a quick health overview of your New Relic-monitored applications
---

# New Relic Status Overview

Get a quick health check across your New Relic-monitored applications.

## Instructions

1. Verify environment variables:
```bash
test -n "$NEW_RELIC_API_KEY" && test -n "$NEW_RELIC_ACCOUNT_ID" && echo "OK" || echo "MISSING: set NEW_RELIC_API_KEY and NEW_RELIC_ACCOUNT_ID"
```

2. Run these queries to build the overview:

**Application health (error rate + throughput):**
```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d "{\"query\": \"{ actor { account(id: $NEW_RELIC_ACCOUNT_ID) { nrql(query: \\\"SELECT rate(count(*), 1 minute) AS 'rpm', percentage(count(*), WHERE error IS TRUE) AS 'error_pct', average(duration) AS 'avg_duration' FROM Transaction FACET appName SINCE 30 minutes ago\\\") { results } } } }\"}" \
  | python3 -m json.tool
```

**Active alerts:**
```bash
curl -s -X GET 'https://api.newrelic.com/v2/alerts_violations.json?only_open=true' \
  -H "Api-Key: $NEW_RELIC_API_KEY" \
  | python3 -m json.tool
```

**Infrastructure summary:**
```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d "{\"query\": \"{ actor { account(id: $NEW_RELIC_ACCOUNT_ID) { nrql(query: \\\"SELECT average(cpuPercent) AS 'cpu', average(memoryUsedPercent) AS 'memory' FROM SystemSample FACET hostname SINCE 30 minutes ago\\\") { results } } } }\"}" \
  | python3 -m json.tool
```

3. Present a concise status dashboard:

```
## System Status

### Applications
| App | RPM | Error % | Avg Duration |
|-----|-----|---------|-------------|

### Active Alerts
- [count] open violations (or "None")

### Infrastructure
| Host | CPU % | Memory % |
|------|-------|----------|
```
