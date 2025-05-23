# MCP (Multi-Component Protocol) Modules

This directory contains the foundation for MCP connections and a test server/client.

## Overview
- `foundation.py`: Contains the `MCPConnection` class for interacting with MCP servers.
- `test_server.py`: A simple FastAPI-based MCP server with token authentication for testing.
- `test_client.py`: A script to test and demonstrate the usage of `MCPConnection` with `test_server.py`.

## Running the Test Server

1.  **Ensure dependencies are installed**:
    ```bash
    pip install -r ../requirements.txt 
    ```
    (Assuming you are in the `mcp` directory, otherwise adjust path to `requirements.txt`)

2.  **Start the server**:
    From the project root directory:
    ```bash
    uvicorn mcp.test_server:app --reload --port 8000
    ```
    The server will be available at `http://127.0.0.1:8000`.

3.  **Test Token**:
    The server uses a hardcoded bearer token for authentication. The token is defined in `mcp.test_server.py` as `TEST_TOKEN`.
    Currently, it is: `test_token_123`.

## Running the Test Client

1.  **Ensure the test server is running** (see above).

2.  **Execute the client script**:
    From the project root directory:
    ```bash
    python -m mcp.test_client
    ```
    The client will attempt to connect to the server, make a few test requests (including one with an invalid token), and print the results.

## Running Unit Tests

To run the unit tests for the MCP modules:

1.  **Ensure dependencies are installed** (including `requests`, `fastapi`, `httpx`). If you are in the `mcp` directory:
    ```bash
    pip install -r ../requirements.txt 
    ```
    Or from the project root:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Navigate to the project root directory.** (The tests are designed to be run from there).

3.  **Execute the tests**:
    ```bash
    python -m unittest discover -s tests -p 'test_*.py'
    ```
    This command will discover and run all test files (matching `test_*.py`) in the `tests` directory.
