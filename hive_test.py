from hive_metastore_client import HiveMetastoreClient

def test_hive_metastore_connection():
    # 1. Create the Hive Metastore client for the container's Thrift port
    client = HiveMetastoreClient('localhost', 9083)
    
    try:
        client.open()
        print("Successfully connected to Hive Metastore!")
        
        # 2. Fetch all available databases
        databases = client.get_all_databases()
        print(f"Available Databases: {databases}")
        
        # 3. Fetch tables inside the default database
        if 'default' in databases:
            tables = client.get_all_tables('default')
            print(f"Tables in 'default': {tables}")
    except Exception as e:
        print(f"Failed to communicate with Hive Metastore: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    test_hive_metastore_connection()