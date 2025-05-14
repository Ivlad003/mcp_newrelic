[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/ivlad003-mcp-newrelic-badge.png)](https://mseep.ai/app/ivlad003-mcp-newrelic)

# New Relic MCP Server

A simple Model Context Protocol (MCP) server for querying New Relic logs using NRQL queries. This server enables Large Language Models (LLMs) like Claude to interact with your New Relic data.

## Features

- Query New Relic logs and metrics using NRQL
- Detailed error logging
- Easy integration with Claude Desktop
- Human-readable output formatting
- Configurable New Relic account ID

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- New Relic account and API key
- Claude Desktop application

### Installation Steps

1. Install `uv` package manager:
```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Create and setup project:
```bash
# Create directory
mkdir newrelic-mcp
cd newrelic-mcp

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows

# Install dependencies
uv pip install "mcp[cli]" httpx
```

3. Create server file `newrelic_logs_server.py` with the provided code.

4. Configure your environment variables:
```bash
# On Unix/macOS
export NEW_RELIC_API_KEY="your-api-key-here"
export NEW_RELIC_ACCOUNT_ID="your-account-id-here"

# On Windows (CMD)
set NEW_RELIC_API_KEY=your-api-key-here
set NEW_RELIC_ACCOUNT_ID=your-account-id-here

# On Windows (PowerShell)
$env:NEW_RELIC_API_KEY = "your-api-key-here"
$env:NEW_RELIC_ACCOUNT_ID = "your-account-id-here"
```

### Claude Desktop Integration

Configure Claude Desktop by editing your configuration file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following configuration:
```json
{
    "mcpServers": {
        "newrelic": {
            "command": "uv",
            "args": [
                "--directory",
                "/absolute/path/to/newrelic-mcp",
                "run",
                "newrelic_logs_server.py"
            ],
            "env": {
                "NEW_RELIC_API_KEY": "your-api-key-here",
                "NEW_RELIC_ACCOUNT_ID": "your-account-id-here"
            }
        }
    }
}
```

## Usage

### Example NRQL Queries

1. Basic Transaction Query:
```sql
SELECT * FROM Transaction SINCE 1 hour ago
```

2. Error Analysis:
```sql
SELECT * FROM Transaction WHERE error IS TRUE SINCE 1 hour ago LIMIT 10
```

3. Performance Analysis:
```sql
SELECT average(duration) FROM Transaction FACET name ORDER BY average(duration) DESC LIMIT 5
```

### Example Claude Prompts

You can ask Claude questions like:
- "Show me all transactions from the last hour"
- "Are there any errors in our application?"
- "What are our slowest endpoints?"

## Debugging

### Viewing Logs

```bash
# On macOS/Linux
tail -f ~/Library/Logs/Claude/mcp-server-newrelic.log

# On Windows
type %APPDATA%\Claude\logs\mcp-server-newrelic.log
```

### Testing with MCP Inspector

Test your server functionality using:
```bash
npx @modelcontextprotocol/inspector uv run newrelic_logs_server.py
```

### Common Issues

1. Authentication Errors:
- Check if NEW_RELIC_API_KEY is set correctly
- Verify API key has correct permissions
- Ensure API key is valid

2. Query Errors:
- Verify NRQL syntax
- Check account ID in code matches your account
- Ensure queried data exists in the time range

3. Connection Issues:
- Check network connectivity
- Verify GraphQL endpoint is accessible
- Ensure no firewalls are blocking connections

## Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- Keep dependencies updated
- Monitor query patterns and access logs

## Development

### Local Testing

1. Set environment variables:
```bash
export NEW_RELIC_API_KEY="your-api-key-here"
export NEW_RELIC_ACCOUNT_ID="your-account-id-here"
```

2. Run the server:
```bash
uv run newrelic_logs_server.py
```

### Code Structure

The server implements:
- Single NRQL query tool
- Configurable New Relic account ID
- Comprehensive error handling
- Detailed logging
- Response formatting

### Testing Changes

1. Modify code as needed
2. Test with MCP Inspector
3. Restart Claude Desktop to apply changes

## Troubleshooting Guide

1. Server Not Starting:
- Check Python version
- Verify all dependencies are installed
- Ensure virtual environment is activated

2. Query Not Working:
- Check logs for detailed error messages
- Verify NRQL syntax
- Ensure data exists in queried time range

3. Claude Not Connecting:
- Verify configuration file syntax
- Check paths are absolute
- Restart Claude Desktop

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

If you encounter issues:
1. Check the logs
2. Review common issues section
3. Test with MCP Inspector
4. File an issue on GitHub