# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install uv
RUN pip install uv

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt using uv
# Using --system to install in the global site-packages, common for containers
# Using --no-cache to reduce image size
RUN uv pip install --system -r requirements.txt --no-cache

# Copy the rest of the application code into the container at /app
# Ensure all necessary directories and files for the main app are copied.
# This includes backend, frontend, prompts, data, and any root-level .py files if necessary.
COPY backend/ ./backend
COPY frontend/ ./frontend
COPY prompts/ ./prompts
COPY data/ ./data
# If there are other root-level files like main.py or utils.py that are part of the app, copy them too.
# COPY main.py . 
# COPY utils.py .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable (example, can be overridden in docker-compose)
ENV NAME World

# Run app.py when the container launches
# Replace backend.main:app with your actual application entry point
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
