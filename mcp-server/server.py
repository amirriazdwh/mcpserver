import os
from mcp.server.fastmcp import FastMCP
from hive_metastore_client import HiveMetastoreClient

# Initialize the MCP server
mcp = FastMCP("Hive-Metadata-Context")

# Get host from environment variable, defaulting to the docker-compose service name
HIVE_HOST = os.getenv("HIVE_HOST", "hive-metastore")
HIVE_PORT = int(os.getenv("HIVE_PORT", 9083))


def _normalize_name(value: str) -> str:
    return value.strip().lower()


def _is_table_not_found_error(error: Exception) -> bool:
    message = str(error).lower()
    markers = ("nosuchobject", "not found", "does not exist", "unknown table")
    return any(marker in message for marker in markers)


def _try_get_table(client, database_name: str, table_name: str):
    try:
        return client.get_table(database_name, table_name)
    except Exception as exc:
        if _is_table_not_found_error(exc):
            return None
        raise

def get_client():
    client = HiveMetastoreClient(HIVE_HOST, HIVE_PORT)
    client.open()
    return client


def _build_schema_payload(table, include_partitions: bool = True) -> dict:
    schema = {col.name: col.type for col in table.sd.cols}
    if include_partitions and table.partitionKeys:
        schema["_PARTITIONS_"] = {col.name: col.type for col in table.partitionKeys}
    return schema

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
        return _build_schema_payload(table, include_partitions=True)
    finally:
        client.close()


@mcp.tool()
def find_table(
    table_name: str,
    database_name: str | None = None,
    exact_match: bool = False,
    max_results: int = 25,
) -> list[dict]:
    """Find matching table names across one database or all databases."""
    target = _normalize_name(table_name)
    client = get_client()
    try:
        # Fast path for exact lookups: call metastore directly instead of scanning tables.
        if exact_match:
            if database_name:
                table = _try_get_table(client, database_name, table_name)
                if not table:
                    return []
                return [
                    {
                        "database_name": database_name,
                        "table_name": table.tableName,
                        "match_type": "exact",
                    }
                ]

            results = []
            for db in client.get_all_databases():
                table = _try_get_table(client, db, table_name)
                if table:
                    results.append(
                        {
                            "database_name": db,
                            "table_name": table.tableName,
                            "match_type": "exact",
                        }
                    )
            return results[:max_results]

        databases = [database_name] if database_name else client.get_all_databases()
        results = []

        for db in databases:
            for table in client.get_all_tables(db):
                current = _normalize_name(table)
                if current == target:
                    match_type = "exact"
                elif current.startswith(target):
                    match_type = "prefix"
                elif target in current:
                    match_type = "contains"
                else:
                    continue

                results.append(
                    {
                        "database_name": db,
                        "table_name": table,
                        "match_type": match_type,
                    }
                )

        rank = {"exact": 0, "prefix": 1, "contains": 2}
        results.sort(
            key=lambda item: (
                rank.get(item["match_type"], 99),
                item["database_name"],
                item["table_name"],
            )
        )
        return results[:max_results]
    finally:
        client.close()


@mcp.tool()
def find_table_schema(
    table_name: str,
    database_name: str | None = None,
    include_partitions: bool = True,
) -> dict:
    """Find a table and return its schema without requiring an exact database first."""
    matches = find_table(
        table_name=table_name,
        database_name=database_name,
        exact_match=True,
        max_results=50,
    )

    if not matches:
        raise ValueError(
            f"No table named '{table_name}' was found"
            + (f" in database '{database_name}'" if database_name else " in any database")
            + "."
        )

    if len(matches) > 1:
        candidates = [f"{row['database_name']}.{row['table_name']}" for row in matches]
        raise ValueError(
            "Table name is ambiguous across databases. "
            f"Please provide database_name. Matches: {candidates}"
        )

    match = matches[0]
    client = get_client()
    try:
        table = client.get_table(match["database_name"], match["table_name"])
        return {
            "database_name": match["database_name"],
            "table_name": match["table_name"],
            "schema": _build_schema_payload(table, include_partitions=include_partitions),
        }
    finally:
        client.close()


@mcp.tool()
def find_table_partitions(database_name: str, table_name: str, max_results: int = 100) -> dict:
    """Get partition columns and current partition names for a specific table."""
    client = get_client()
    try:
        table = client.get_table(database_name, table_name)
        partition_columns = [
            {"name": col.name, "type": col.type} for col in (table.partitionKeys or [])
        ]

        if not partition_columns:
            return {
                "database_name": database_name,
                "table_name": table_name,
                "is_partitioned": False,
                "partition_columns": [],
                "partition_count": 0,
                "partitions": [],
            }

        partition_names = client.get_partition_names(database_name, table_name, max_results)
        return {
            "database_name": database_name,
            "table_name": table_name,
            "is_partitioned": True,
            "partition_columns": partition_columns,
            "partition_count": len(partition_names),
            "partitions": partition_names,
        }
    finally:
        client.close()

if __name__ == "__main__":
    # Run over standard IO for Cline compatibility
    mcp.run()