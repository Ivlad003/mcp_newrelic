---
name: newrelic-ops
description: Use when the user asks about New Relic data — application performance, errors, alerts, deployments, infrastructure, logs, NRQL queries, dashboards, or production incidents. Calls New Relic APIs directly via curl. Triggers on keywords like "new relic", "nrql", "apm", "alert violations", "error rate", "throughput", "transactions", "deployment markers".
---

# New Relic Operations

Call New Relic NerdGraph (GraphQL) and REST v2 APIs directly via `curl`. No MCP server or Python dependencies needed.

## Prerequisites

Two environment variables must be set:
- `NEW_RELIC_API_KEY` — User API key (starts with `NRAK-`)
- `NEW_RELIC_ACCOUNT_ID` — Numeric account ID

Before the first API call in a session, verify they exist:
```bash
test -n "$NEW_RELIC_API_KEY" && test -n "$NEW_RELIC_ACCOUNT_ID" && echo "OK" || echo "MISSING: set NEW_RELIC_API_KEY and NEW_RELIC_ACCOUNT_ID"
```

If missing, ask the user to set them. Do NOT proceed without them.

## API Endpoints

| API | Endpoint | Auth Header |
|-----|----------|-------------|
| NerdGraph (GraphQL) US | `https://api.newrelic.com/graphql` | `API-Key: $NEW_RELIC_API_KEY` |
| NerdGraph (GraphQL) EU | `https://api.eu.newrelic.com/graphql` | `API-Key: $NEW_RELIC_API_KEY` |
| REST v2 US | `https://api.newrelic.com/v2/` | `Api-Key: $NEW_RELIC_API_KEY` |

Default to US endpoints. If the user mentions EU region, switch to EU endpoints.

## Core Operations

### 1. Run NRQL Query (most common)

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d "{\"query\": \"{ actor { account(id: $NEW_RELIC_ACCOUNT_ID) { nrql(query: \\\"SELECT count(*) FROM Transaction SINCE 1 HOUR AGO\\\") { results } } } }\"}" \
  | python3 -m json.tool
```

Replace the NRQL inside `\\\"...\\\"` with the user's query.

**Common NRQL event types:**

| Event Type | Data |
|-----------|------|
| `Transaction` | APM request data (duration, status, name) |
| `TransactionError` | Errors with stack traces |
| `Log` | Log entries |
| `SystemSample` | Host CPU/memory/disk |
| `Metric` | Dimensional metrics |
| `SyntheticCheck` | Synthetic monitor results |
| `NrAiIncident` | Alert incidents |
| `Deployment` | Change tracking events |

**NRQL essentials:**
- Always include a time range: `SINCE 1 hour ago`, `SINCE 1 day ago`
- Use `FACET` for grouping: `FACET appName`, `FACET host`
- Use `TIMESERIES` for trends over time
- Use `LIMIT` to control result size (default 10)
- Use `WHERE error IS TRUE` to filter errors
- Use `COMPARE WITH 1 hour ago` to compare periods

### 2. Search Entities (apps, hosts, dashboards)

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{"query": "{ actor { entitySearch(queryBuilder: {domain: APM, type: APPLICATION}) { results { entities { name entityType guid accountId alertSeverity reporting } nextCursor } } } }"}' \
  | python3 -m json.tool
```

**Domain/Type combinations:**

| Domain | Type | What |
|--------|------|------|
| `APM` | `APPLICATION` | APM applications |
| `INFRA` | `HOST` | Infrastructure hosts |
| `BROWSER` | `APPLICATION` | Browser apps |
| `MOBILE` | `APPLICATION` | Mobile apps |
| `VIZ` | `DASHBOARD` | Dashboards |
| `SYNTH` | `MONITOR` | Synthetic monitors |

**Search by name (freeform):**
```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d "{\"query\": \"{ actor { entitySearch(query: \\\"name LIKE 'SERVICE_NAME' AND domain = 'APM'\\\") { count results { entities { name guid entityType alertSeverity } } } } }\"}" \
  | python3 -m json.tool
```

### 3. Get Entity Details by GUID

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{"query": "{ actor { entity(guid: \"ENTITY_GUID_HERE\") { name entityType alertSeverity ... on ApmApplicationEntityOutline { apmSummary { errorRate apdexScore webResponseTimeAverage responseTimeAverage throughput hostCount instanceCount } } } } }"}' \
  | python3 -m json.tool
```

### 4. Get Active Alerts

**Via REST v2 (simpler):**
```bash
curl -s -X GET 'https://api.newrelic.com/v2/alerts_violations.json?only_open=true' \
  -H "Api-Key: $NEW_RELIC_API_KEY" \
  | python3 -m json.tool
```

**Via NRQL (more flexible):**
```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d "{\"query\": \"{ actor { account(id: $NEW_RELIC_ACCOUNT_ID) { nrql(query: \\\"SELECT * FROM NrAiIncident WHERE event = 'open' SINCE 1 day ago LIMIT 50\\\") { results } } } }\"}" \
  | python3 -m json.tool
```

### 5. Get Error Traces

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d "{\"query\": \"{ actor { account(id: $NEW_RELIC_ACCOUNT_ID) { nrql(query: \\\"SELECT * FROM TransactionError SINCE 1 hour ago LIMIT 20\\\") { results } } } }\"}" \
  | python3 -m json.tool
```

**Useful error queries:**
- Error rate by app: `SELECT rate(count(*), 1 minute) FROM TransactionError FACET appName SINCE 30 minutes ago`
- Error messages: `SELECT count(*) FROM TransactionError FACET error.message SINCE 1 hour ago`
- Error trend: `SELECT rate(count(*), 1 minute) FROM TransactionError TIMESERIES SINCE 1 hour ago`

### 6. List Deployments

```bash
curl -s -X GET "https://api.newrelic.com/v2/applications/APP_ID/deployments.json" \
  -H "Api-Key: $NEW_RELIC_API_KEY" \
  | python3 -m json.tool
```

To get `APP_ID`, first list entities (operation 2) with domain `APM`.

### 7. Record a Deployment

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{"query": "mutation { changeTrackingCreateDeployment(deployment: { version: \"VERSION\", entityGuid: \"ENTITY_GUID\", description: \"DESCRIPTION\", user: \"USER\" }) { deploymentId entityGuid } }"}' \
  | python3 -m json.tool
```

### 8. Get Dashboard Details

First find the dashboard GUID (operation 2 with domain `VIZ`), then:

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{"query": "{ actor { entity(guid: \"DASHBOARD_GUID\") { ... on DashboardEntity { name description pages { name widgets { title rawConfiguration } } } } } }"}' \
  | python3 -m json.tool
```

### 9. List Applications (REST v2)

```bash
curl -s -X GET 'https://api.newrelic.com/v2/applications.json' \
  -H "Api-Key: $NEW_RELIC_API_KEY" \
  | python3 -m json.tool
```

### 10. Infrastructure / Host Metrics

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d "{\"query\": \"{ actor { account(id: $NEW_RELIC_ACCOUNT_ID) { nrql(query: \\\"SELECT average(cpuPercent), average(memoryUsedPercent), average(diskUsedPercent) FROM SystemSample FACET hostname SINCE 1 hour ago\\\") { results } } } }\"}" \
  | python3 -m json.tool
```

### 11. Alert Policies

```bash
curl -s -X GET 'https://api.newrelic.com/v2/alerts_policies.json' \
  -H "Api-Key: $NEW_RELIC_API_KEY" \
  | python3 -m json.tool
```

### 12. Logs

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d "{\"query\": \"{ actor { account(id: $NEW_RELIC_ACCOUNT_ID) { nrql(query: \\\"SELECT * FROM Log WHERE level = 'ERROR' SINCE 1 hour ago LIMIT 50\\\") { results } } } }\"}" \
  | python3 -m json.tool
```

## Investigation Workflows

### Incident Investigation
1. Check active alerts (operation 4)
2. Query recent errors (operation 5)
3. Correlate with deployments (operation 6)
4. Check infrastructure metrics (operation 10)
5. Review logs around incident time (operation 12)

### Performance Analysis
1. Slow endpoints: `SELECT average(duration) FROM Transaction FACET name ORDER BY average(duration) DESC LIMIT 10 SINCE 1 hour ago`
2. P95 latency: `SELECT percentile(duration, 95) FROM Transaction FACET name SINCE 1 hour ago`
3. Throughput: `SELECT rate(count(*), 1 minute) FROM Transaction TIMESERIES SINCE 1 hour ago`
4. Compare with baseline: `SELECT average(duration) FROM Transaction SINCE 1 hour ago COMPARE WITH 1 day ago`

### Error Triage
1. Error rate trend: `SELECT rate(count(*), 1 minute) FROM TransactionError TIMESERIES SINCE 1 hour ago`
2. Group by message: `SELECT count(*) FROM TransactionError FACET error.message LIMIT 20 SINCE 1 hour ago`
3. Affected endpoints: `SELECT count(*) FROM TransactionError FACET request.uri SINCE 1 hour ago`
4. Error vs success ratio: `SELECT percentage(count(*), WHERE error IS TRUE) FROM Transaction FACET name SINCE 1 hour ago`

## Output Handling

- Always pipe curl output through `| python3 -m json.tool` for readable formatting
- For extracting just NRQL results, use:
  ```bash
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('data',{}).get('actor',{}).get('account',{}).get('nrql',{}).get('results',[]), indent=2))"
  ```
- Present results to the user in a clean table or summary — don't dump raw JSON unless asked

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid or expired API key | Check `NEW_RELIC_API_KEY` |
| 403 Forbidden | Key lacks permissions | User needs admin or appropriate role |
| GraphQL errors in response | Bad NRQL or invalid account ID | Check `errors` field, fix query syntax |
| Empty results | No data in time range | Widen time range with `SINCE` |
| Connection refused | Network issue | Check connectivity to `api.newrelic.com` |
