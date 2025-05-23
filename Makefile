.PHONY: install run-app run-mcp-server run-dev-servers test smoke-test clean

# Variables (adjust if your environment uses uv for execution directly)
PYTHON = python
UVICORN = uvicorn

# Check for requirements-dev.txt
REQUIREMENTS_DEV_EXISTS = $(wildcard requirements-dev.txt)

install:
	@echo "Installing dependencies..."
	uv pip install -r requirements.txt
ifdef REQUIREMENTS_DEV_EXISTS
	uv pip install -r requirements-dev.txt
else
	@echo "requirements-dev.txt not found, skipping."
endif

run-app:
	@echo "Starting main application (Recipe Chatbot) on http://127.0.0.1:8000..."
	$(UVICORN) backend.main:app --host 127.0.0.1 --port 8000 --reload

run-mcp-server:
	@echo "Starting MCP Test Server on http://127.0.0.1:8001..."
	$(UVICORN) mcp.test_server:app --host 127.0.0.1 --port 8001 --reload

run-dev-servers:
	@echo "To run the development servers, please open two separate terminals."
	@echo "In the first terminal, run: make run-app"
	@echo "In the second terminal, run: make run-mcp-server"

test:
	@echo "Running unit tests..."
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

smoke-test:
	@echo "Running smoke tests..."
	@echo "Please ensure both development servers are running first (using 'make run-dev-servers' instructions)."
	$(PYTHON) scripts/smoke_test.py

clean:
	@echo "Cleaning up Python bytecode and cache files..."
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
	@echo "Clean up complete."

help:
	@echo "Available targets:"
	@echo "  install           - Install project dependencies"
	@echo "  run-app           - Start the main application"
	@echo "  run-mcp-server    - Start the MCP test server"
	@echo "  run-dev-servers   - Instructions to start both development servers"
	@echo "  test              - Run unit tests"
	@echo "  smoke-test        - Run smoke tests (requires servers to be running)"
	@echo "  clean             - Remove Python bytecode and cache files"
	@echo "  help              - Show this help message"
