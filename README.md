# Hive Store

## Start Hive services

Create the shared network if it does not already exist:

```bash
docker network create hive_net
```

Start Hive and metastore services using the `hive-server` component compose file:

```bash
docker compose -f hive-server/docker-compose.yml up -d
```

## Start MCP server

After Hive services are running, start the MCP service from the `mcp-server` component directory:

```bash
docker compose -f mcp-server/docker-compose.yml up -d
```

## Access Hive Metadata via MCP Server

The MCP server provides three tools for accessing Hive metadata:

- **list_databases()** - Returns all available databases
- **list_tables(database_name)** - Lists tables in a specific database
- **get_table_schema(database_name, table_name)** - Returns column names and types

Example from Python:

```python
import sys
sys.path.insert(0, 'mcp-server')
from server import list_databases, list_tables, get_table_schema

# List all databases
databases = list_databases()
print(databases)  # ['default', 'financial_lake']

# List tables in financial_lake
tables = list_tables('financial_lake')
print(tables)  # ['dim_customer', 'fact_transaction']

# Get table schema
schema = get_table_schema('financial_lake', 'dim_customer')
print(schema)  # {'customer_id': 'int', 'first_name': 'string', 'last_name': 'string'}
```

**Note:** HiveServer2 (port 10000) support is available but not currently the primary interface. The MCP server connects directly to the Hive Metastore Thrift service (port 9083) which is fully operational.

## Stop services

```bash
docker compose -f hive-server/docker-compose.yml down
```

```bash
docker compose -f mcp-server/docker-compose.yml down
```

## Sanity testing

From the repository root, install development dependencies and run the Hive integration test:

```bash
cd /home/amirriaz/hive-store
python3 -m pip install -r requirements-dev.txt
pytest tests/test_hive_integration.py
```

To verify the MCP server tool functions directly:

```bash
cd /home/amirriaz/hive-store
. .venv/bin/activate
python tests/verify_mcp_server.py
```

## List running containers

```bash
docker ps
```

# mcpserver

