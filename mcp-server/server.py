import os
from mcp.server.fastmcp import FastMCP
from hive_metastore_client import HiveMetastoreClient

# Initialize the MCP server
mcp = FastMCP("Hive-Metadata-Context")

# Get host from environment variable, defaulting to the docker-compose service name
HIVE_HOST = os.getenv("HIVE_HOST", "hive-metastore")
HIVE_PORT = int(os.getenv("HIVE_PORT", 9083))

def get_client():
    client = HiveMetastoreClient(HIVE_HOST, HIVE_PORT)
    client.open()
    return client

@mcp.tool()
def list_databases() -> list[str]:
    """Get all available databases in the Hive Data Lake."""
    client = get_client()
    try:
        return client.get_all_databases()
    finally:
        client.close()

@mcp.tool()
def list_tables(database_name: str) -> list[str]:
    """Get all tables within a specific database (e.g., 'financial_lake')."""
    client = get_client()
    try:
        return client.get_all_tables(database_name)
    finally:
        client.close()

@mcp.tool()
def get_table_schema(database_name: str, table_name: str) -> dict:
    """Get the exact column names and data types for a specific table."""
    client = get_client()
    try:
        table = client.get_table(database_name, table_name)
        schema = {col.name: col.type for col in table.sd.cols}
        
        # Include partition keys if it's a partitioned table (like fact_transaction)
        if table.partitionKeys:
            schema["_PARTITIONS_"] = {col.name: col.type for col in table.partitionKeys}
            
        return schema
    finally:
        client.close()

if __name__ == "__main__":
    # Run over standard IO for Cline compatibility
    mcp.run()