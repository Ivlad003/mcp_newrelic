---
description: Run an NRQL query against New Relic and display results
---

# New Relic Query

Run the provided NRQL query against New Relic's NerdGraph API.

## Instructions

1. First verify environment variables are set:
```bash
test -n "$NEW_RELIC_API_KEY" && test -n "$NEW_RELIC_ACCOUNT_ID" && echo "OK" || echo "MISSING: set NEW_RELIC_API_KEY and NEW_RELIC_ACCOUNT_ID"
```

2. Take the user's NRQL query (provided as the argument to this command). If no query is provided, ask the user what they want to query.

3. Execute the query:
```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d "{\"query\": \"{ actor { account(id: $NEW_RELIC_ACCOUNT_ID) { nrql(query: \\\"USER_NRQL_QUERY_HERE\\\") { results } } } }\"}" \
  | python3 -m json.tool
```

4. Present the results in a clean, readable format (table or summary). Don't dump raw JSON unless the user asks for it.
