# Hive Store

Complete Hive + MCP metadata stack with PostgreSQL-backed persistence. ✅ **All components functional and data persists across container restarts.**

## Architecture

- **PostgreSQL** (port 5432): Persistent metastore backend with named volume
- **Hive Metastore** (port 9083): Thrift service for metadata access
- **HiveServer2** (port 10000): JDBC interface for Beeline/SQL access
- **MCP Server** (optional): Model Context Protocol server for Claude integration

## Quick Start

### 1. Start Hive Stack

```bash
docker compose -f hive-server/docker-compose.yml up -d
```

This starts:
- PostgreSQL metastore database
- Hive Metastore service (port 9083)
- HiveServer2 JDBC service (port 10000)

### 2. Verify Services Running

```bash
docker ps
```

You should see 3 containers: `hive-server`, `hive-metastore`, `hive-metastore-db`

### 3. Create Sample Schema (Optional)

```bash
docker exec hive-server beeline -u jdbc:hive2://hive-server:10000 -e "
CREATE DATABASE IF NOT EXISTS financial_lake;
USE financial_lake;
CREATE TABLE dim_customer (customer_id INT, first_name STRING, last_name STRING);
CREATE TABLE fact_transaction (transaction_id STRING, customer_id INT, amount DOUBLE);
"
```

### 4. Test Persistence

Restart containers and verify schema persists:

```bash
docker compose -f hive-server/docker-compose.yml restart
docker exec hive-server beeline -u jdbc:hive2://hive-server:10000 -e "SHOW DATABASES;"
```

✅ Both `default` and `financial_lake` will still exist.

## Persistence Guarantee

✅ **Schema persists across all restarts** because:
- PostgreSQL data stored in named volume `hive-db-data` (mounted to `/var/lib/postgresql/data`)
- HiveServer2 uses PostgreSQL backend (not local Derby)
- Hive Metastore also uses same PostgreSQL backend
- No data loss on container restart or rebuild

## Access Methods

### Method 1: Beeline/HiveServer2 (JDBC)

Interactive Beeline session:

```bash
docker exec -it hive-server beeline -u jdbc:hive2://hive-server:10000
```

Non-interactive queries:

```bash
docker exec hive-server beeline -u jdbc:hive2://hive-server:10000 -e "SHOW DATABASES;"
```

Beeline SQL examples:

```sql
-- Show all databases
SHOW DATABASES;

-- Create and use a database  
CREATE DATABASE financial_lake;
USE financial_lake;

-- Create tables
CREATE TABLE dim_customer (customer_id INT, first_name STRING, last_name STRING);
CREATE TABLE fact_transaction (transaction_id STRING, customer_id INT, amount DOUBLE);

-- List and describe
SHOW TABLES;
DESCRIBE dim_customer;

-- Query
SELECT * FROM dim_customer LIMIT 5;
```

### Method 2: MCP Server Tools (Recommended for Claude Integration)

The MCP server provides three tools via the Hive Metastore Thrift service (port 9083):

```bash
docker compose -f mcp-server/docker-compose.yml up -d
```

Python example:

```python
import sys
import os
sys.path.insert(0, 'mcp-server')
os.environ['HIVE_HOST'] = 'localhost'
os.environ['HIVE_PORT'] = '9083'

from server import list_databases, list_tables, get_table_schema

# List all databases
databases = list_databases()  # ['default', 'financial_lake']

# List tables
tables = list_tables('financial_lake')  # ['dim_customer', 'fact_transaction']

# Get table schema
schema = get_table_schema('financial_lake', 'dim_customer')
# {'customer_id': 'int', 'first_name': 'string', 'last_name': 'string'}
```

Verify MCP server:

```bash
. .venv/bin/activate
python tests/verify_mcp_server.py
```

### Method 3: Python Hive Metastore Client

Direct Thrift client access:

```python
from hive_metastore_client import HiveMetastoreClient

client = HiveMetastoreClient('localhost', 9083)
client.open()

# Get databases
databases = client.get_all_databases()  # ['default', 'financial_lake']

# Get tables
tables = client.get_all_tables('financial_lake')  # ['dim_customer', 'fact_transaction']

# Get table schema
table = client.get_table('financial_lake', 'dim_customer')
columns = [(col.name, col.type) for col in table.sd.cols]
# [('customer_id', 'int'), ('first_name', 'string'), ('last_name', 'string')]

client.close()
```

## Network Note

⚠️ **HiveServer2 Access:**
- ✅ Use `docker exec -it hive-server beeline` from host (seamless)
- ✅ Use `hive-server:10000` from within Docker containers
- ❌ Cannot use `localhost:10000` from host directly (container isolation)

## Testing

### Run All Tests

```bash
. .venv/bin/activate
python tests/verify_mcp_server.py   # MCP server verification
pytest tests/test_hive_integration.py  # Integration tests
```

### Manual Verification

```bash
# Check Hive services
docker ps | grep -E "hive|postgres"

# Verify PostgreSQL persistence
docker exec hive-metastore-db psql -U hive metastore_db -c 'SELECT "NAME" FROM "DBS";'

# Verify MCP can access metadata
docker exec hive-server beeline -u jdbc:hive2://hive-server:10000 -e "SHOW DATABASES;"
```

## Stop Services

Hive stack:

```bash
docker compose -f hive-server/docker-compose.yml down
```

MCP server:

```bash
docker compose -f mcp-server/docker-compose.yml down
```

Keep PostgreSQL data (restart-safe):

```bash
docker compose -f hive-server/docker-compose.yml restart
```

## Component Details

| Component | Port | Status | Notes |
|-----------|------|--------|-------|
| PostgreSQL | 5432 | ✅ Internal | Persistent volume: `hive-db-data` |
| Hive Metastore | 9083 | ✅ Thrift | Uses PostgreSQL backend |
| HiveServer2 | 10000 | ✅ JDBC | Uses PostgreSQL backend |
| MCP Server | - | Optional | Requires separate `docker compose up` |

## Data Persistence

✅ **Guaranteed Persistence:**
- All databases created via Beeline persist to PostgreSQL
- All tables and columns persist
- Schema survives container restarts, reboots, and `docker compose down`
- PostgreSQL volume `hive-db-data` mounted persistently

❌ **Not Persistent:**
- In-memory caches (automatically refreshed on reconnect)
- Temporary query results
- HiveServer2 session state

## Troubleshooting

**Schema not showing after restart?**
- Check PostgreSQL volume: `docker volume ls | grep hive-db-data`
- Verify connection: `docker exec hive-metastore-db psql -U hive metastore_db -c "\dt"`

**Beeline connection refused?**
- Verify containers running: `docker ps | grep hive`
- Check HiveServer2 logs: `docker logs hive-server | tail -20`

**MCP server not starting?**
- Run after Hive stack is running
- Check MCP logs: `docker logs mcp-server | tail -20`

