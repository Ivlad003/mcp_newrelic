import os
import sys
import httpx
from mcp.server.fastmcp import FastMCP
import logging

# Initialize FastMCP server
mcp = FastMCP("newrelic-logs")

# Configure logging. stdio transport uses stdout for JSON-RPC, so logs must go
# to stderr (basicConfig default). Keep the level quiet to avoid dumping full
# response bodies on every call.
logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Constants
NR_GRAPHQL_URL = "https://api.newrelic.com/graphql"
DEFAULT_ACCOUNT_ID = os.getenv("NEW_RELIC_ACCOUNT_ID", "1892029")

# GraphQL document. The NRQL string is passed as a variable so quotes, newlines,
# or braces in the query can never break the surrounding document.
NRQL_QUERY_DOCUMENT = """
query ($accountId: Int!, $nrql: Nrql!) {
    actor {
        account(id: $accountId) {
            nrql(query: $nrql) {
                results
            }
        }
    }
}
"""

# One client for the whole process. Creating and tearing down an
# httpx.AsyncClient on every call is wasteful and, under some event-loop
# teardown paths, can raise during __aexit__ and destabilise the session.
_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client

@mcp.tool()
async def query_logs(query: str, account_id: str = DEFAULT_ACCOUNT_ID) -> str:
    """Query New Relic logs using NRQL.

    Args:
        query: NRQL query string (e.g., "SELECT * FROM Transaction")
        account_id: New Relic account ID (default from env var)
    """
    api_key = os.getenv("NEW_RELIC_API_KEY")
    if not api_key:
        return "Error: NEW_RELIC_API_KEY environment variable is not set"

    try:
        account_id_int = int(account_id)
    except (TypeError, ValueError):
        return f"Error: account_id must be numeric, got {account_id!r}"

    headers = {
        "Content-Type": "application/json",
        "API-Key": api_key,
    }

    payload = {
        "query": NRQL_QUERY_DOCUMENT,
        "variables": {"accountId": account_id_int, "nrql": query},
    }

    try:
        client = _get_client()
        response = await client.post(NR_GRAPHQL_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # Check for errors in the response
        if "errors" in result:
            logger.warning("GraphQL errors: %s", result["errors"])
            return f"GraphQL errors: {result['errors']}"

        # Extract logs from response
        data = result.get("data")
        if data is None:
            return "Error: No 'data' field in response"

        account = data.get("actor", {}).get("account")
        if account is None:
            return "Error: No 'account' field in 'actor'"

        nrql = account.get("nrql")
        if nrql is None:
            return "Error: No 'nrql' field in 'account'"

        logs = nrql.get("results", [])

        # Format the logs into a readable string
        formatted_logs = []
        for log in logs:
            formatted_logs.append("---\n" + "\n".join(f"{k}: {v}" for k, v in log.items()))

        return "\n".join(formatted_logs) if formatted_logs else "No logs found"
    except Exception as e:
        logger.warning("Error querying logs: %s", str(e))
        return f"Error querying logs: {str(e)}"


if __name__ == "__main__":
    mcp.run()