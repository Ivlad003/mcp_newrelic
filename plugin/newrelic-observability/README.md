# New Relic Plugin for Claude Code

Query and analyze New Relic observability data directly from Claude Code using direct REST API calls. No MCP server or extra dependencies needed.

## Prerequisites

Set these environment variables before using:

```bash
export NEW_RELIC_API_KEY="NRAK-your-key-here"
export NEW_RELIC_ACCOUNT_ID="your-account-id"
```

## Installation

### From GitHub

```bash
/plugin marketplace add ivlad003/plugins
/plugin install newrelic-observability@ivlad-plugins
```

### From local directory

```bash
claude plugin install ./plugin/newrelic-observability
```

## What's Included

### Slash Commands

| Command | Description |
|---------|-------------|
| `/nr-query <NRQL>` | Run any NRQL query and get formatted results |
| `/nr-alerts` | Check active alert violations |
| `/nr-status` | Quick health overview of all monitored apps |
| `/nr-investigate` | Full incident investigation with root cause analysis |

### Skill: `newrelic-ops`

Automatically activated when you ask about New Relic data. Gives Claude knowledge of 12 API operations:

1. Run NRQL queries
2. Search entities (apps, hosts, dashboards, monitors)
3. Get entity details (error rate, apdex, throughput)
4. Check active alerts
5. Get error traces
6. List deployments
7. Record deployments
8. Get dashboard details
9. List applications
10. Infrastructure/host metrics
11. Alert policies
12. Log queries

Plus 3 investigation workflows: Incident, Performance, and Error Triage.

### Agent: `newrelic-investigator`

A specialized agent for production incident investigation. Correlates alerts, errors, latency, deployments, and infrastructure metrics to find root causes. Produces structured incident summaries.

## Usage Examples

```
# Direct questions (skill activates automatically)
"What's the error rate for my-app in the last hour?"
"Show me the slowest endpoints"
"Are there any open alerts?"
"What deployments happened today?"

# Slash commands
/nr-status
/nr-alerts
/nr-query SELECT count(*) FROM Transaction FACET appName SINCE 1 hour ago
/nr-investigate the checkout service is returning 500s
```

## How It Works

This plugin instructs Claude to call New Relic APIs directly using `curl`:
- **NerdGraph (GraphQL)**: `https://api.newrelic.com/graphql` for NRQL queries, entity search, deployments
- **REST v2**: `https://api.newrelic.com/v2/` for alerts, applications

No Python, no MCP server, no extra processes — just `curl` and your API key.

## License

MIT License
