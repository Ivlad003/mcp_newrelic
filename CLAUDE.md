# MCP NewRelic

Two ways to use New Relic with Claude — pick one or both.

## Environment Variables

- `NEW_RELIC_API_KEY` — Required. New Relic User API key (starts with `NRAK-`).
- `NEW_RELIC_ACCOUNT_ID` — Required. Numeric New Relic account ID.

## Option 1: MCP Server (`app.py`)

Traditional MCP server for Claude Desktop and MCP-compatible clients. Runs as a Python process.

- Single tool: `query_logs` — runs NRQL queries via NerdGraph GraphQL API
- Requires Python 3.13+, httpx, mcp[cli], pydantic
- Run with: `uv run app.py`

## Option 2: Claude Code Plugin (`plugin/`)

Installable plugin for Claude Code CLI. Uses direct REST API calls via curl — no Python, no MCP server needed.

- 4 slash commands: `/nr-query`, `/nr-alerts`, `/nr-status`, `/nr-investigate`
- 1 skill: `newrelic-ops` (12 API operations, 3 investigation workflows)
- 1 agent: `newrelic-investigator` (incident root cause analysis)
- Plugin repo: https://github.com/Ivlad003/plugins
- Install: `/plugin marketplace add Ivlad003/plugins`

## Project Structure

```
app.py                          # MCP server (Option 1)
pyproject.toml                  # Python project config for MCP server
plugin/
  newrelic-observability/       # Claude Code plugin (Option 2)
    commands/                   # /nr-query, /nr-alerts, /nr-status, /nr-investigate
    agents/                     # newrelic-investigator
    skills/newrelic-ops/        # 12 API operations + workflows
.claude-plugin/
  marketplace.json              # Marketplace: ivlad-plugins
```
