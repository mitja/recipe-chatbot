# Recipe Chatbot

> 📝 **Note:** This project serves as a foundation for ongoing development throughout the AI Evals course. We will be incrementally adding features and refining its capabilities in subsequent lessons and homework assignments.

This project provides a starting point for building and evaluating an AI-powered Recipe Chatbot. You will be working with a web application that uses FastAPI for the backend and a simple HTML/CSS/JavaScript frontend. The core of the chatbot involves interacting with a Large Language Model (LLM) via LiteLLM to get recipe recommendations.

Your main tasks will be to refine the chatbot's persona and intelligence by crafting a detailed system prompt, expanding its test query dataset, and evaluating its performance.

![Recipe Chatbot UI](./screenshots/hw1.png)

## Table of Contents

- [Core Components Provided](#core-components-provided)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Running the Provided Application](#running-the-provided-application)
  - [1. Run the Web Application (Frontend and Backend)](#1-run-the-web-application-frontend-and-backend)
  - [2. Run the Bulk Test Script](#2-run-the-bulk-test-script)
- [Homework Assignment 1: Write a Starting Prompt](#homework-assignment-1-write-a-starting-prompt)

## Core Components Provided

This initial setup includes:

*   **Backend (FastAPI)**: Serves the frontend and provides an API endpoint (`/chat`) for the chatbot logic.
*   **Frontend (HTML/CSS/JS)**: A basic, modern chat interface where users can send messages and receive responses.
    *   Renders assistant responses as Markdown.
    *   Includes a typing indicator for better user experience.
*   **LLM Integration (LiteLLM)**: The backend connects to an LLM (configurable via `.env`) to generate recipe advice.
*   **Bulk Testing Script**: A Python script (`scripts/bulk_test.py`) to send multiple predefined queries (from `data/sample_queries.csv`) to the chatbot's core logic and save the responses for evaluation. This script uses `rich` for pretty console output.

## Project Structure

```
recipe-chatbot/
├── backend/
│   ├── __init__.py
│   ├── main.py         # FastAPI application, routes
│   └── utils.py        # LiteLLM wrapper, system prompt, env loading
├── data/
│   └── sample_queries.csv # Sample queries for bulk testing (ID, Query)
├── frontend/
│   └── index.html      # Chat UI (HTML, CSS, JavaScript)
├── results/            # Output folder for bulk_test.py
├── scripts/
│   └── bulk_test.py    # Bulk testing script
├── .env.example        # Example environment file
├── env.example         # Backup env example (can be removed if .env.example is preferred)
├── requirements.txt    # Python dependencies
└── README.md           # This file (Your guide!)
```

## Using Makefile

A `Makefile` is provided to simplify common development tasks. Here are some of the available targets:

*   **`make install`**:
    Installs all necessary project dependencies from `requirements.txt` and `requirements-dev.txt` (if present) using `uv pip install`.

*   **`make run-app`**:
    Starts the main Recipe Chatbot application. It will be available at `http://127.0.0.1:8000`. The server will auto-reload on code changes.

*   **`make run-mcp-server`**:
    Starts the MCP (Multi-Component Protocol) test server. It will be available at `http://127.0.0.1:8001`. This server will also auto-reload on code changes.

*   **`make run-dev-servers`**:
    Provides instructions to run both `make run-app` and `make run-mcp-server` in separate terminals for a complete development environment.

*   **`make test`**:
    Runs all unit tests located in the `tests/` directory.

*   **`make smoke-test`**:
    Runs the smoke test script (`scripts/smoke_test.py`). Make sure you have started the development servers (e.g., by following `make run-dev-servers` instructions) before running this.

*   **`make clean`**:
    Removes Python bytecode files (`.pyc`, `.pyo`) and `__pycache__` directories from the project.

*   **`make help`**:
    Displays a list of all available targets and their descriptions.

To use a target, simply run `make <target-name>` from the project root directory (e.g., `make install`).

## Setup Instructions

1.  **Clone the Repository (if you haven't already)**
    ```bash
    git clone https://github.com/ai-evals-course/recipe-chatbot.git
    cd recipe-chatbot
    ```

2.  **Create and Activate a Python Virtual Environment**
    ```bash
    python -m venv .venv
    ```
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    
    > **Note**: The `requirements.txt` includes dependencies for all homework assignments, including advanced evaluation tools like `judgy` for LLM-as-Judge workflows (Homework 3) and machine learning libraries for data analysis.

4.  **Configure Environment Variables (`.env` file)**
    *   Copy the example environment file:
        ```bash
        cp env.example .env
        ```
        (or `cp .env.example .env` if you have that one)
    *   Edit the `.env` file. You will need to:
        1.  Set the `MODEL_NAME` to the specific model you want to use (e.g., `openai/gpt-4.1-nano`, `anthropic/claude-3-opus-20240229`, `ollama/llama2`).
        2.  Set the **appropriate API key environment variable** for the chosen model provider. 
            Refer to your `env.example` for common API key names like `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, etc. 
            LiteLLM will automatically use these provider-specific keys.

        Example of a configured `.env` file if using an OpenAI model:
        ```env
        MODEL_NAME=openai/gpt-4.1-nano
        OPENAI_API_KEY=sk-yourActualOpenAIKey...
        ```
        Example for an Anthropic model:
        ```env
        MODEL_NAME=anthropic/claude-3-haiku-20240307
        ANTHROPIC_API_KEY=sk-ant-yourActualAnthropicKey...
        ```

    *   **Important - Model Naming and API Keys with LiteLLM**:
        LiteLLM supports a wide array of model providers. To use a model from a specific provider, you generally need to:
        *   **Prefix the `MODEL_NAME`** correctly (e.g., `openai/`, `anthropic/`, `mistral/`, `ollama/`).
        *   **Set the corresponding API key variable** in your `.env` file (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MISTRAL_API_KEY`). Some local models like Ollama might not require an API key.

        Please refer to the official LiteLLM documentation for the correct model prefixes and required environment variables for your chosen provider: [LiteLLM Supported Providers](https://docs.litellm.ai/docs/providers).

## Development Setup with `uv`

`uv` is an extremely fast Python package installer and resolver, written in Rust. It can be used as a drop-in replacement for `pip` and `venv`.

**Installation**: To install `uv`, please refer to the official installation guide: [https://astral.sh/docs/uv/installation](https://astral.sh/docs/uv/installation)

**Creating a Virtual Environment**:
```bash
# Create a virtual environment in a .venv directory
uv venv
```

**Activating the Virtual Environment**:
*   On macOS and Linux:
    ```bash
    source .venv/bin/activate
    ```
*   On Windows (Command Prompt):
    ```bash
    .venv\Scripts\activate.bat
    ```
*   On Windows (PowerShell):
    ```bash
    .venv\Scripts\Activate.ps1
    ```

**Installing Dependencies**:
```bash
# Install main dependencies
uv pip install -r requirements.txt
# Install development dependencies (including uv itself for consistency if desired, or other dev tools)
uv pip install -r requirements-dev.txt
```

**(Optional) Running the Application/Scripts with `uv`**:
You can also use `uv run` to execute scripts or applications within the managed environment without explicitly activating it:
```bash
# Example: Run the test MCP server (from project root)
uv run uvicorn mcp.test_server:app --reload --port 8001

# Example: Run the test MCP client (from project root)
uv run python -m mcp.test_client

# Example: Run unit tests (from project root)
uv run python -m unittest discover -s tests -p 'test_*.py'
```

## Running with Docker Compose

This project is configured to run with Docker Compose, allowing for an isolated and consistent environment for the main application and the MCP test server.

### Prerequisites

*   **Docker Desktop** (or Docker Engine + Docker Compose CLI) installed. You can download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/).

### Build and Start Services

To build the Docker images and start the services, navigate to the project root directory and run:

```bash
docker-compose up --build
```

For detached mode (to run in the background), use:
```bash
docker-compose up --build -d
```

### Accessing Services

Once the services are running:

*   **Main Application (Recipe Chatbot)**: Accessible at [http://localhost:8000](http://localhost:8000)
*   **MCP Test Server**: Accessible at [http://localhost:8001](http://localhost:8001)
    *   The test server expects a Bearer token for authentication. The token is defined in `mcp/test_server.py` (currently `test_token_123`).

### Viewing Logs

To view the logs from the running services:

```bash
# View logs for all services
docker-compose logs -f

# View logs for a specific service (e.g., app or mcp_server)
docker-compose logs -f app
docker-compose logs -f mcp_server
```

### Stopping Services

To stop and remove the containers, networks, and volumes created by `docker-compose up`:

```bash
docker-compose down
```

To stop services without removing them (so they can be restarted quickly):
```bash
docker-compose stop
```

### Running Tests with Docker Compose (Optional Example)

If you need to run unit tests within the Docker environment of the `app` service:
```bash
docker-compose exec app uv run python -m unittest discover -s tests -p 'test_*.py'
```
This command executes the test discovery inside the `app` container.

### Running the Smoke Test

After starting the Docker Compose stack, you can run a smoke test script to verify that both the main application and the MCP test server are reachable and responding correctly.

1.  **Ensure the Docker Compose stack is running**:
    Make sure services are up, preferably in detached mode:
    ```bash
    docker-compose up --build -d
    ```
    Allow a few moments for the services to initialize, especially on the first run. The smoke test script has built-in retries, but services should ideally be stable.

2.  **Run the smoke test script**:
    Execute the script from the project root:
    ```bash
    python scripts/smoke_test.py
    ```
    Or, using `uv` if your environment is set up with it:
    ```bash
    uv run python scripts/smoke_test.py
    ```
    The script will output the status of its checks and exit with code 0 if all tests pass, or 1 if any test fails.

3.  **(Optional) Bring down the stack**:
    After testing, you can bring down the services:
    ```bash
    docker-compose down
    ```

## Running the Provided Application

### 1. Run the Web Application (Frontend and Backend)

*   Ensure your virtual environment is activated and your `.env` file is configured.
*   From the project root directory, start the FastAPI server using Uvicorn:
    ```bash
    uvicorn backend.main:app --reload
    ```
*   Open your web browser and navigate to: `http://127.0.0.1:8000`

    You should see the chat interface.

#### Managing Family Data (via Function Calling)

The chatbot can now understand requests related to managing family information and will use backend tools to interact with a database. This is achieved through an LLM function-calling mechanism.

You can try prompts like:

*   "Please create a family named The Jetsons with the slug 'jetsons'."
*   "Can you add a member named George to the family 'jetsons'? His age is 40 and he is male." 
    *   (You can also specify height, weight, and target caloric intake: e.g., "height 175 cm, weight 70 kg, target calories 2200")
*   "Show me a summary of members in the 'jetsons' family."

The chatbot will use tools to perform these actions and then confirm the outcome or provide the requested information. This demonstrates a more advanced interaction where the LLM can leverage structured data operations.

**Note**: For these features to work:
*   The database must be initialized (e.g., `make install` followed by Alembic migrations if you set up the DB manually, or `docker-compose up` which uses a pre-configured DB in its volume).
*   The `DATABASE_URL` environment variable must be correctly configured for the backend to connect to the database.


### 2. Run the Bulk Test Script

The bulk test script allows you to evaluate your chatbot's responses to a predefined set of queries. It sends queries from `data/sample_queries.csv` directly to the backend agent logic and saves the responses to the `results/` directory.

*   Ensure your virtual environment is activated and your `.env` file is configured.
*   From the project root directory, run:
    ```bash
    python scripts/bulk_test.py
    ```
*   To use a different CSV file for queries:
    ```bash
    python scripts/bulk_test.py --csv path/to/your/queries.csv
    ```
    The CSV file must have `id` and `query` columns.
*   Check the `results/` folder for a new CSV file containing the IDs, queries, and their corresponding responses. This will be crucial for evaluating your system prompt changes.

---
