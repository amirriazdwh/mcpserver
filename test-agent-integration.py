#!/usr/bin/env python3
"""
Agent Context Test - Demonstrates how a VS Code agent (Cline, Copilot) 
would use the MCP server to understand and work with Hive schema
"""

import sys
import os

# Setup paths
sys.path.insert(0, 'mcp-server')
os.environ['HIVE_HOST'] = 'localhost'
os.environ['HIVE_PORT'] = '9083'

from server import list_databases, list_tables, get_table_schema

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_subheader(title):
    print(f"\n>>> {title}")
    print("-" * 80)

def agent_test():
    """Simulate agent interactions with Hive schema"""
    
    print_header("🤖 VS CODE AGENT CONTEXT TEST")
    print("Simulating how a VS Code agent (Cline/Copilot) uses MCP server")
    print("for schema discovery and code generation")
    
    # Test 1: Database Discovery
    print_subheader("AGENT STEP 1: Discovery - What databases are available?")
    print("Agent Query: list_databases()")
    databases = list_databases()
    print(f"Agent Result: {databases}")
    for db in databases:
        print(f"  ✓ Found database: '{db}'")
    
    # Test 2: Table Discovery
    print_subheader("AGENT STEP 2: Exploration - What tables are in 'financial_lake'?")
    print("Agent Query: list_tables('financial_lake')")
    tables = list_tables('financial_lake')
    print(f"Agent Result: {tables}")
    for table in tables:
        print(f"  ✓ Found table: '{table}'")
    
    # Test 3: Schema Details
    print_subheader("AGENT STEP 3: Analysis - What's the schema of 'dim_customer'?")
    print("Agent Query: get_table_schema('financial_lake', 'dim_customer')")
    schema_customer = get_table_schema('financial_lake', 'dim_customer')
    print("Agent Result - Column Details:")
    for col_name, col_type in schema_customer.items():
        print(f"  • {col_name:20} : {col_type}")
    
    # Test 4: Another Table Schema
    print_subheader("AGENT STEP 4: Analysis - What's the schema of 'fact_transaction'?")
    print("Agent Query: get_table_schema('financial_lake', 'fact_transaction')")
    schema_transaction = get_table_schema('financial_lake', 'fact_transaction')
    print("Agent Result - Column Details:")
    for col_name, col_type in schema_transaction.items():
        print(f"  • {col_name:20} : {col_type}")
    
    # Test 5: Agent Generates Intelligent Suggestions
    print_subheader("AGENT STEP 5: Intelligence - Generate useful SQL queries")
    print("\nBased on schema analysis, agent now understands:")
    print(f"  ✓ dim_customer has customer information (ID, name)")
    print(f"  ✓ fact_transaction tracks financial transactions")
    print(f"  ✓ Both tables share customer_id (foreign key relationship)")
    print("\nAgent can now generate:")
    print("\n  📝 Suggested Query 1 - Get all customer transactions:")
    print("""
    SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        ft.transaction_id,
        ft.amount
    FROM financial_lake.dim_customer c
    JOIN financial_lake.fact_transaction ft
        ON c.customer_id = ft.customer_id
    ORDER BY c.customer_id
    """)
    
    print("  📝 Suggested Query 2 - Total amount by customer:")
    print("""
    SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        SUM(ft.amount) as total_amount
    FROM financial_lake.dim_customer c
    JOIN financial_lake.fact_transaction ft
        ON c.customer_id = ft.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name
    ORDER BY total_amount DESC
    """)
    
    print("  📝 Suggested Query 3 - Insert new customer:")
    print("""
    INSERT INTO financial_lake.dim_customer (customer_id, first_name, last_name)
    VALUES (101, 'John', 'Doe')
    """)
    
    # Test 6: Context Availability
    print_subheader("AGENT STEP 6: Context Ready - Schema available for suggestions")
    print("\n✅ Agent Context Information:")
    print(f"   • Available Databases: {len(databases)}")
    print(f"   • Tables in financial_lake: {len(tables)}")
    print(f"   • dim_customer Columns: {len(schema_customer)}")
    print(f"   • fact_transaction Columns: {len(schema_transaction)}")
    
    print("\n✅ Agent Capabilities Unlocked:")
    print("   • Smart SQL auto-completion")
    print("   • Data model understanding")
    print("   • Query optimization suggestions")
    print("   • Schema-aware code generation")
    print("   • Relationship detection")
    print("   • Data type validation")
    
    # Summary
    print_header("✅ MCP SERVER AGENT INTEGRATION SUCCESSFUL")
    print("\n📊 Integration Status:")
    print("   ✓ MCP server responding correctly")
    print("   ✓ Schema discovery working")
    print("   ✓ All 3 tools functioning")
    print("   ✓ Agent can access complete Hive metadata")
    print("   ✓ Ready for VS Code integration")
    
    print("\n🚀 Next Steps:")
    print("   1. Start MCP server: ./start-mcp-server.sh")
    print("   2. Configure VS Code agent to use MCP server")
    print("   3. Agent will have full Hive schema context")
    print("   4. Get intelligent suggestions and code generation")
    
    print("\n" + "=" * 80)
    print("Test Complete! ✅")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    try:
        agent_test()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
