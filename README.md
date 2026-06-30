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

## Access Hive via Beeline (HiveServer2) ✅ WORKING

### Quick Start: Connect to HiveServer2

**From your host machine:**

```bash
docker exec -it hive-server beeline -u jdbc:hive2://hive-server:10000
```

**Interactive Beeline session:**

```bash
docker exec -it hive-server beeline -u jdbc:hive2://hive-server:10000
```

Then run Hive SQL commands like:

```sql
-- Show all databases
SHOW DATABASES;

-- Create and use a database  
CREATE DATABASE IF NOT EXISTS financial_lake;
USE financial_lake;

-- Create tables
CREATE TABLE dim_customer (
  customer_id INT,
  first_name STRING,
  last_name STRING
);

CREATE TABLE fact_transaction (
  transaction_id STRING,
  customer_id INT,
  amount DOUBLE
);

-- List tables
SHOW TABLES;

-- Describe table schema
DESCRIBE dim_customer;

-- Query data
SELECT * FROM dim_customer LIMIT 5;
```

### Non-interactive Beeline Commands

Execute SQL directly without opening interactive session:

```bash
docker exec hive-server beeline -u jdbc:hive2://hive-server:10000 -e "SHOW DATABASES;"
```

```bash
docker exec hive-server beeline -u jdbc:hive2://hive-server:10000 -e "
CREATE DATABASE IF NOT EXISTS mydb;
USE mydb;
CREATE TABLE mytable (id INT, name STRING);
SHOW TABLES;
"
```

### Important Notes

⚠️ **HiveServer2 binding note:** HiveServer2 binds to the container's internal network interface. To connect:
- ✅ From host: Use `docker exec -it hive-server beeline` or connect within Docker network
- ❌ Cannot connect directly to `jdbc:hive2://localhost:10000` from host machine
- ✅ Can connect to `jdbc:hive2://hive-server:10000` from containers in same network
- ✅ Can use `docker exec` for seamless access from host

### Alternative: Use Python Hive Metastore Client

For programmatic access, use the Python client directly:

```python
from hive_metastore_client import HiveMetastoreClient

client = HiveMetastoreClient('localhost', 9083)
try:
    client.open()
    databases = client.get_all_databases()
    tables = client.get_all_tables('financial_lake')
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

