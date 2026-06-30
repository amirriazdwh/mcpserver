#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Ensure HIVE_HOST/HIVE_PORT are set before importing server.py
os.environ.setdefault("HIVE_HOST", "localhost")
os.environ.setdefault("HIVE_PORT", "9083")

# Ensure the MCP server package is importable from the project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "mcp-server"))

from server import list_databases, list_tables


def main() -> int:
    hive_host = os.getenv("HIVE_HOST")
    hive_port = os.getenv("HIVE_PORT")
    print(f"Testing MCP server tool functions against Hive metastore at {hive_host}:{hive_port}")

    try:
        databases = list_databases()
        print("Databases:", databases)

        if "financial_lake" not in databases:
            print("ERROR: financial_lake database not found")
            return 1

        tables = list_tables("financial_lake")
        print("financial_lake tables:", tables)

        expected = {"dim_customer", "fact_transaction"}
        missing = expected - set(tables)
        if missing:
            print(f"ERROR: Missing expected tables: {sorted(missing)}")
            return 1

        print("MCP server verification succeeded.")
        return 0
    except Exception as e:
        print("MCP server verification failed:", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
