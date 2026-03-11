# ta-lib-mcp

Read-only Python MCP server for TA-Lib indicator discovery and computation.

## What It Exposes

- `talib_list_indicators`: list available indicators with group, category, and search filters.
- `talib_get_indicator_info`: inspect one indicator's inputs, outputs, parameters, and category.
- `talib_compute_indicator`: compute an indicator from numeric OHLCV-like arrays.
- `talib_list_categories`: list indicator categories (Trend, Momentum, Volume, etc.) with descriptions.
- `talib_get_version_info`: report MCP, Python, and TA-Lib versions.

## Requirements

- Python 3.13+
- `mcp[cli]`
- Optional: `TA-Lib` (`pip install "ta-lib-mcp-server[talib]"`)

If TA-Lib is missing, the server still starts and returns actionable errors for TA-Lib tools.

## Install

```bash
pip install -e ".[dev,talib]"
```

## Run

```bash
ta-lib-mcp
```

## MCP Client Configuration

### Claude Desktop

```json
{
  "mcpServers": {
    "ta-lib": {
      "command": "ta-lib-mcp",
      "env": {
        "TALIB_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Codex

```toml
[mcp_servers.talib]
command = "ta-lib-mcp"
args = []

[mcp_servers.talib.env]
TALIB_MCP_LOG_LEVEL = "INFO"
```

### Gemini CLI

```json
{
  "mcpServers": {
    "ta-lib": {
      "command": "ta-lib-mcp",
      "env": {
        "TALIB_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Development

```bash
pip install -e ".[dev,talib]"
pytest
ruff check src tests
ruff format src tests
mypy src
```

## Engineering Rules

- Read-only server behavior only; no stateful or exchange-connected operations.
- External MCP tool inputs are validated in `src/ta_lib_mcp/validators.py`.
- Do not use `eval` or `exec`.
