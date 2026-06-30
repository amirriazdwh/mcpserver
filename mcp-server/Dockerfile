FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir mcp hive-metastore-client

# Copy the server script
COPY server.py .

# Standard IO requires no buffering to work properly with MCP
ENV PYTHONUNBUFFERED=1

# Run the server
ENTRYPOINT ["python", "server.py"]