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

4.  **Configure Environment Variables (`.env` file)**
    *   Copy the example environment file:
        ```bash
        cp env.example .env
        ```
        (or `cp .env.example .env` if you have that one)
    *   Edit the `.env` file. You will need to:
        1.  Set the `MODEL_NAME` to the specific model you want to use (e.g., `openai/gpt-3.5-turbo`, `anthropic/claude-3-opus-20240229`, `ollama/llama2`).
        2.  Set the **appropriate API key environment variable** for the chosen model provider. 
            Refer to your `env.example` for common API key names like `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, etc. 
            LiteLLM will automatically use these provider-specific keys.

        Example of a configured `.env` file if using an OpenAI model:
        ```env
        MODEL_NAME=openai/gpt-3.5-turbo
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
uv run uvicorn mcp.test_server:app --reload --port 8000

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

## Running the Provided Application

### 1. Run the Web Application (Frontend and Backend)

*   Ensure your virtual environment is activated and your `.env` file is configured.
*   From the project root directory, start the FastAPI server using Uvicorn:
    ```bash
    uvicorn backend.main:app --reload
    ```
*   Open your web browser and navigate to: `http://127.0.0.1:8000`

    You should see the chat interface.


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

## Homework Assignment 1: Write a Starting Prompt

Your main task is to get the repo to a starting point for Lesson 2.

1.  **Write an Effective System Prompt**:
    *   Open `backend/utils.py` and locate the `SYSTEM_PROMPT` constant. Currently, it's a naive placeholder.
    *   Replace it with a well-crafted system prompt. Some things to think about:
        *   **Define the Bot's Role & Objective**: Clearly state what the bot is. (e.g., "You are a friendly and creative culinary assistant specializing in suggesting easy-to-follow recipes.")
        *   **Instructions & Response Rules**: Be specific.
            *   What should it *always* do? (e.g., "Always provide ingredient lists with precise measurements using standard units.", "Always include clear, step-by-step instructions.")
            *   What should it *never* do? (e.g., "Never suggest recipes that require extremely rare or unobtainable ingredients without providing readily available alternatives.", "Never use offensive or derogatory language.")
            *   Safety Clause: (e.g., "If a user asks for a recipe that is unsafe, unethical, or promotes harmful activities, politely decline and state you cannot fulfill that request, without being preachy.")
        *   **LLM Agency – How Much Freedom?**:
            *   Define its creativity level. (e.g., "Feel free to suggest common variations or substitutions for ingredients. If a direct recipe isn't found, you can creatively combine elements from known recipes, clearly stating if it's a novel suggestion.")
            *   Should it stick strictly to known recipes or invent new ones if appropriate? (Be explicit).
        *   **Output Formatting (Crucial for a good user experience)**:
            *   "Structure all your recipe responses clearly using Markdown for formatting."
            *   "Begin every recipe response with the recipe name as a Level 2 Heading (e.g., `## Amazing Blueberry Muffins`)."
            *   "Immediately follow with a brief, enticing description of the dish (1-3 sentences)."
            *   "Next, include a section titled `### Ingredients`. List all ingredients using a Markdown unordered list (bullet points)."
            *   "Following ingredients, include a section titled `### Instructions`. Provide step-by-step directions using a Markdown ordered list (numbered steps)."
            *   "Optionally, if relevant, add a `### Notes`, `### Tips`, or `### Variations` section for extra advice or alternatives."
            *   **Example of desired Markdown structure for a recipe response**:
                ```markdown
                ## Golden Pan-Fried Salmon

                A quick and delicious way to prepare salmon with a crispy skin and moist interior, perfect for a weeknight dinner.

                ### Ingredients
                * 2 salmon fillets (approx. 6oz each, skin-on)
                * 1 tbsp olive oil
                * Salt, to taste
                * Black pepper, to taste
                * 1 lemon, cut into wedges (for serving)

                ### Instructions
                1. Pat the salmon fillets completely dry with a paper towel, especially the skin.
                2. Season both sides of the salmon with salt and pepper.
                3. Heat olive oil in a non-stick skillet over medium-high heat until shimmering.
                4. Place salmon fillets skin-side down in the hot pan.
                5. Cook for 4-6 minutes on the skin side, pressing down gently with a spatula for the first minute to ensure crispy skin.
                6. Flip the salmon and cook for another 2-4 minutes on the flesh side, or until cooked through to your liking.
                7. Serve immediately with lemon wedges.

                ### Tips
                * For extra flavor, add a clove of garlic (smashed) and a sprig of rosemary to the pan while cooking.
                * Ensure the pan is hot before adding the salmon for the best sear.
                ```

2.  **Expand and Diversify the Query Dataset**:
    *   Open `data/sample_queries.csv`.
    *   Add at least **10 new, diverse queries** to this file. Ensure each new query has a unique `id` and a corresponding query text.
    *   Your queries should test various aspects of a recipe chatbot. Consider including requests related to:
        *   Specific cuisines (e.g., "Italian pasta dish", "Spicy Thai curry")
        *   Dietary restrictions (e.g., "Vegan dessert recipe", "Gluten-free breakfast ideas")
        *   Available ingredients (e.g., "What can I make with chicken, rice, and broccoli?")
        *   Meal types (e.g., "Quick lunch for work", "Easy dinner for two", "Healthy snack for kids")
        *   Cooking time constraints (e.g., "Recipe under 30 minutes")
        *   Skill levels (e.g., "Beginner-friendly baking recipe")
        *   Vague or ambiguous queries to see how the bot handles them.
    * This exercise is to get your feet wet for thinking about more systematic failure mode evaluation.

3.  **Run the Bulk Test & Evaluate**:
    *   After you have updated the system prompt in `backend/utils.py` and expanded the queries in `data/sample_queries.csv`, run the bulk test script:
        ```bash
        python scripts/bulk_test.py
        ```
    * Make sure a new CSV has been written.
    
Good luck!