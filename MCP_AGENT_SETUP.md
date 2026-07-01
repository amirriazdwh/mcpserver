# MCP Server Setup for VS Code Agents

This document explains how to configure the Hive MCP server for use with VS Code agents (GitHub Copilot, Cline, etc.).

## Architecture

```
VS Code Agent (Copilot/Cline)
    ↓ (via MCP protocol)
Hive MCP Server (localhost:5000)
    ↓ (Thrift protocol)
Hive Metastore (port 9083)
    ↓ (JDBC/SQL)
HiveServer2 (port 10000) + PostgreSQL
```

## Prerequisites

✅ Hive Stack running:
```bash
docker compose -f hive-store/docker-compose.yml up -d
```

✅ MCP Server running (local or Docker):
```bash
# Option 1: Run locally in virtualenv
cd hive-store
. .venv/bin/activate
cd mcp-server
python -m mcp.server.stdio server:mcp

# Option 2: Run in Docker (once Docker credential issue is fixed)
cd hive-store
docker compose -f mcp-server/docker-compose.yml up -d
```

## For VS Code Agents (Cline, Copilot, etc.)

### Option A: Stdio Transport (Recommended)

Add to your VS Code settings or agent configuration:

```json
{
  "mcpServers": {
    "hive-metadata": {
      "command": "python",
      "args": [
        "-m",
        "mcp.server.stdio",
        "path/to/mcp-server/server:mcp"
      ],
      "env": {
        "HIVE_HOST": "localhost",
        "HIVE_PORT": "9083"
      }
    }
  }
}
```

### Option B: HTTP Transport (Alternative)

If using HTTP-based agents, expose the server:

```bash
# Option 1: Use FastMCP HTTP mode
python mcp-server/server.py --host 0.0.0.0 --port 5000

# Option 2: Proxy with simple HTTP wrapper
pip install fastmcp
# Create a wrapper that exposes HTTP endpoint
```

## Testing

The MCP server provides core metadata tools to agents:

### 1. list_databases()
Returns all available Hive databases
```python
# Agent calls this to understand available datasets
result: ["default", "financial_lake"]
```

### 2. list_tables(database_name: str)
Lists all tables in a specific database
```python
# Agent calls this for schema discovery
list_tables("financial_lake")
result: ["dim_customer", "fact_transaction"]
```

### 3. get_table_schema(database_name: str, table_name: str)
Returns column names and data types
```python
# Agent calls this to understand table structure
get_table_schema("financial_lake", "dim_customer")
result: {
  "customer_id": "int",
  "first_name": "string", 
  "last_name": "string"
}
```

### 4. find_table(table_name: str, database_name: str | None = None, exact_match: bool = False)
Find matching table names across one database or all databases
```python
find_table("customer")
result: [
  {"database_name": "financial_lake", "table_name": "dim_customer", "match_type": "contains"}
]
```

### 5. find_table_schema(table_name: str, database_name: str | None = None, include_partitions: bool = True)
Find a table by name and return schema, even when database is not provided
```python
find_table_schema("dim_customer")
result: {
  "database_name": "financial_lake",
  "table_name": "dim_customer",
  "schema": {"customer_id": "int", "first_name": "string", "last_name": "string"}
}
```

### 6. find_table_partitions(database_name: str, table_name: str, max_results: int = 100)
Get partition columns and current partition names for a table
```python
find_table_partitions("financial_lake", "fact_transaction")
result: {
  "is_partitioned": false,
  "partition_columns": [],
  "partition_count": 0,
  "partitions": []
}
```

## Current Status

✅ **MCP Server is fully functional and ready for agent integration**

The metadata tools are tested and working. Any MCP-compatible VS Code agent can now:
- Discover all databases
- List tables in any database
- Get complete schema information
- Find tables quickly by partial name
- Inspect partitioning strategy and partitions
- Use this context to provide better suggestions

## Example Agent Usage

When you ask a VS Code agent (like Cline) to help with Hive:

1. **Agent requests context:**
   ```
   "I need to write a query to get all customers"
   ```

2. **Agent calls MCP tools:**
   - `list_databases()` → sees `financial_lake`
  - `find_table("customer")` → sees `financial_lake.dim_customer`
  - `find_table_schema("dim_customer")` → sees all columns
  - `find_table_partitions("financial_lake", "dim_customer")` → sees partition details

3. **Agent provides smart suggestions:**
   ```sql
   SELECT customer_id, first_name, last_name 
   FROM financial_lake.dim_customer
   ```

## Configuration Files

- `.vscode/mcp_config.json` - VS Code agent configuration
- `mcp-server/docker-compose.yml` - Docker deployment config
- `mcp-server/server.py` - MCP server implementation
- `mcp-server/Dockerfile` - Container image

## Troubleshooting

**Agent can't connect to MCP server?**
- Verify Hive services running: `docker ps | grep hive`
- Verify Metastore connectivity: `docker exec hive-metastore nc -zv localhost 9083`
- Check agent configuration paths are correct

**MCP server tools returning empty results?**
- Verify financial_lake database exists
- Create tables if needed (see README.md)
- Check database persistence

**Docker build failing?**
- Fix credential issue: `docker login`
- Or run MCP server locally in virtualenv instead of Docker
