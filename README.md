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

## Connect to HiveServer2 with Beeline

```bash
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000
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
