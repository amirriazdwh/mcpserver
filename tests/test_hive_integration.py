import os
from hive_metastore_client import HiveMetastoreClient


def test_hive_metastore_connection():
    hive_host = os.getenv("HIVE_HOST", "localhost")
    hive_port = int(os.getenv("HIVE_PORT", "9083"))

    client = HiveMetastoreClient(hive_host, hive_port)
    try:
        client.open()

        databases = client.get_all_databases()
        assert isinstance(databases, list)
        assert "default" in databases
        assert "financial_lake" in databases

        default_tables = client.get_all_tables("default")
        assert isinstance(default_tables, list)

        financial_tables = client.get_all_tables("financial_lake")
        assert isinstance(financial_tables, list)
        assert "dim_customer" in financial_tables
        assert "fact_transaction" in financial_tables
    finally:
        client.close()
