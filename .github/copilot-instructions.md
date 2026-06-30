# Copilot Instructions for Hive MCP Context

## MCP-First Rule

When a user asks for SQL, schema, table, or database help in this repository, Copilot must query the Hive MCP tools before answering whenever table structure could matter.

Use the configured MCP server in this workspace (`hive-metadata`) and its tools directly for metadata lookup.
Do not use local helper scripts, test files, or hardcoded schema examples as the primary source when MCP is available.

Required discovery sequence:

1. Call list_databases().
2. Choose the relevant database or ask the user if ambiguous.
3. Call list_tables(database_name).
4. If query uses one or more tables, call get_table_schema(database_name, table_name) for each referenced table.
5. Generate the final answer using discovered names and columns.

## MCP Tool Invocation Rules

- For metadata questions (for example: "what are columns of X", "show table schema", "which tables exist"), use MCP tools directly instead of calling scripts.
- Preferred tools: `list_databases`, `list_tables`, `get_table_schema`.
- Treat script-based methods (for example, importing `mcp-server/server.py`, running test utilities, or parsing README snippets) as fallback only when MCP is unavailable.
- If the user asks for only column names, still run discovery and return just column names (plus types when requested).
- If multiple databases contain similarly named tables, ask the user to choose or provide both matches clearly.

## Fallback Behavior

If MCP tools are unavailable or fail:

- State that MCP lookup failed.
- Share the exact error briefly.
- Provide a clearly marked best-effort answer.
- Ask the user whether to proceed with assumptions.

## SQL Output Rules

- Prefer fully-qualified table names (database.table).
- Do not invent columns.
- If the user says "customer table" and no table with that exact name exists, map to the closest discovered table (for example dim_customer) and state that mapping.

## Verification Preference

When practical, validate generated SQL against Hive via beeline before finalizing.
