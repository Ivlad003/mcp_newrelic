import os
import httpx
from mcp.server.fastmcp import FastMCP
import logging

# Initialize FastMCP server
mcp = FastMCP("newrelic-logs")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
NR_GRAPHQL_URL = "https://api.newrelic.com/graphql"


@mcp.tool()
async def query_logs(query: str) -> str:
    """Query New Relic logs using NRQL.

    Args:
        query: NRQL query string (e.g., "SELECT * FROM Transaction")
    """
    graphql_query = f"""
    {{
        actor {{
            account(id: 1892029) {{
                nrql(query: "{query}") {{
                    results
                }}
            }}
        }}
    }}
    """

    headers = {
        "Content-Type": "application/json",
        "API-Key": os.getenv("NEW_RELIC_API_KEY")
    }

    payload = {
        "query": graphql_query
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                NR_GRAPHQL_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            # Log the full response content
            logger.debug("Response JSON: %s", result)

            # Check for errors in the response
            if "errors" in result:
                logger.error("GraphQL errors: %s", result["errors"])
                return f"GraphQL errors: {result['errors']}"

            # Extract logs from response
            data = result.get("data")
            if data is None:
                logger.error("No 'data' field in response")
                return "Error: No 'data' field in response"

            account = data.get("actor", {}).get("account")
            if account is None:
                logger.error("No 'account' field in 'actor'")
                return "Error: No 'account' field in 'actor'"

            nrql = account.get("nrql")
            if nrql is None:
                logger.error("No 'nrql' field in 'account'")
                return "Error: No 'nrql' field in 'account'"

            logs = nrql.get("results", [])

            # Format the logs into a readable string
            formatted_logs = []
            for log in logs:
                formatted_logs.append("---\n" + "\n".join(f"{k}: {v}" for k, v in log.items()))

            return "\n".join(formatted_logs) if formatted_logs else "No logs found"
    except Exception as e:
        logger.error("Error querying logs: %s", str(e))
        return f"Error querying logs: {str(e)}"


if __name__ == "__main__":
    mcp.run()