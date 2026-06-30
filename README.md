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

## Access Hive Metadata via MCP Server (Recommended)

The MCP server provides three tools for accessing Hive metadata via the Hive Metastore Thrift service (port 9083):

- **list_databases()** - Returns all available databases
- **list_tables(database_name)** - Lists tables in a specific database
- **get_table_schema(database_name, table_name)** - Returns column names and types

Example from Python:

```python
import sys
import os
sys.path.insert(0, 'mcp-server')

# Set connection to localhost for host-based testing
os.environ['HIVE_HOST'] = 'localhost'
os.environ['HIVE_PORT'] = '9083'

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

Run the verification script to test MCP server functionality:

```bash
. .venv/bin/activate
python tests/verify_mcp_server.py
```

## Access Hive via Beeline (HiveServer2)

**⚠️ Current Status:** HiveServer2 (port 10000) is running but not accepting connections. This is a known issue with the current Apache Hive 4.0.0 container configuration.

**Working Alternative:** Use the **MCP Server** (port 9083 - Hive Metastore Thrift) which is fully operational.

### Beeline Commands (for reference):

```bash
# Attempt to connect (will fail in current setup)
docker exec -it hive-server /opt/hive/bin/beeline -u jdbc:hive2://hive-server:10000
```

### Example Beeline SQL Queries:

```sql
-- Show all databases
SHOW DATABASES;

-- Use a specific database
USE financial_lake;

-- Show tables in current database
SHOW TABLES;

-- Show table schema
DESCRIBE dim_customer;

-- Show table details
DESC FORMATTED fact_transaction;

-- Run a query
SELECT * FROM dim_customer LIMIT 5;
```

### Recommended: Use Python Client Instead

Since Beeline/HiveServer2 isn't available, use the Python Hive Metastore client:

```python
from hive_metastore_client import HiveMetastoreClient

client = HiveMetastoreClient('localhost', 9083)
try:
    client.open()
    
    # Get all databases
    databases = client.get_all_databases()
    print(f"Databases: {databases}")
    
    # Get all tables in a database
    tables = client.get_all_tables('financial_lake')
    print(f"Tables: {tables}")
    
    # Get table details
    table = client.get_table('financial_lake', 'dim_customer')
    columns = [(col.name, col.type) for col in table.sd.cols]
    print(f"Columns: {columns}")
    
finally:
    client.close()
```

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

