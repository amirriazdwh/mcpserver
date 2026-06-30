#!/bin/bash

# MCP Server Startup Script for VS Code Agents
# This script starts the Hive MCP server for agent integration

set -e

echo "=========================================="
echo "Hive MCP Server - Agent Integration"
echo "=========================================="
echo ""

# Check if Hive stack is running
echo "✓ Checking Hive services..."
if ! docker ps | grep -q "hive-server\|hive-metastore"; then
    echo "❌ ERROR: Hive services not running!"
    echo ""
    echo "Start with:"
    echo "  docker compose -f hive-server/docker-compose.yml up -d"
    exit 1
fi
echo "✓ Hive services confirmed running"
echo ""

# Activate virtualenv
echo "✓ Activating Python environment..."
cd "$(dirname "$0")"
if [ -f ".venv/bin/activate" ]; then
    . .venv/bin/activate
else
    echo "⚠️  .venv not found, using system Python"
fi
echo ""

# Install MCP if needed
echo "✓ Ensuring MCP is installed..."
pip install -q mcp 2>/dev/null || true
echo ""

# Start MCP server
echo "=========================================="
echo "Starting MCP Server..."
echo "=========================================="
echo ""
echo "MCP Server will be available for agents at:"
echo "  • Stdio transport: mcp-server/server:mcp"
echo "  • HTTP endpoint: localhost:5000 (if using HTTP wrapper)"
echo ""
echo "Three tools available to agents:"
echo "  1. list_databases() - Get all Hive databases"
echo "  2. list_tables(database_name) - List tables in database"
echo "  3. get_table_schema(database_name, table_name) - Get table schema"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run MCP server via stdio
cd mcp-server
python -m mcp.server.stdio server:mcp
