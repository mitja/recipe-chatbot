from __future__ import annotations

"""Utility helpers for the recipe chatbot backend.

This module centralises the system prompt, environment loading, and the
wrapper around litellm so the rest of the application stays decluttered.
"""

import os
from pathlib import Path
from typing import Final, List, Dict

import litellm  # type: ignore
from dotenv import load_dotenv

from mcp.foundation import MCPConnection # Added
from requests.exceptions import HTTPError # Added

# Ensure the .env file is loaded as early as possible.
load_dotenv(override=False)

# --- Constants -------------------------------------------------------------------

_DEFAULT_SYSTEM_PROMPT: str = (
    "You are an expert chef recommending delicious and useful recipes. "
    "Present only one recipe at a time. If the user doesn't specify what ingredients "
    "they have available, assume only basic ingredients are available."
    "Be descriptive in the steps of the recipe, so it is easy to follow."
    "Have variety in your recipes, don't just recommend the same thing over and over."
)

def _load_system_prompt() -> str:
    """Loads system prompt from SYSTEM_PROMPT_PATH or uses default."""
    custom_prompt_path_str = os.environ.get("SYSTEM_PROMPT_PATH")
    if custom_prompt_path_str:
        try:
            # Assuming SYSTEM_PROMPT_PATH is relative to the project root
            project_root = Path.cwd()
            custom_prompt_file = project_root / custom_prompt_path_str
            if custom_prompt_file.exists() and custom_prompt_file.is_file():
                return custom_prompt_file.read_text().strip()
            else:
                # Optionally, log a warning if path is set but file not found
                print(f"Warning: SYSTEM_PROMPT_PATH ('{custom_prompt_path_str}') set, but file not found or not a file. Falling back to default prompt.")
        except Exception as e:
            # Optionally, log the error
            print(f"Warning: Error loading system prompt from '{custom_prompt_path_str}': {e}. Falling back to default prompt.")
    return _DEFAULT_SYSTEM_PROMPT

SYSTEM_PROMPT: str = _load_system_prompt()


# Fetch configuration *after* we loaded the .env file.
MODEL_NAME: Final[str] = os.environ.get("MODEL_NAME", "gpt-4o-mini")


# --- Agent wrapper ---------------------------------------------------------------

def get_agent_response(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:  # noqa: WPS231
    """Call the underlying large-language model via *litellm*.

    Parameters
    ----------
    messages:
        The full conversation history. Each item is a dict with "role" and "content".

    Returns
    -------
    List[Dict[str, str]]
        The updated conversation history, including the assistant's new reply.
    """

    # Make a mutable copy for potential modification with MCP data
    provisional_messages = list(messages) 
    
    # Check for MCP trigger phrase in the last user message
    if provisional_messages and provisional_messages[-1]["role"] == "user":
        user_message_content = provisional_messages[-1]["content"].lower().strip()
        if user_message_content == "show mcp test data":
            mcp_url = os.environ.get("MCP_SERVER_URL")
            mcp_token = os.environ.get("MCP_TEST_TOKEN")
            mcp_info_content = None # To store the content of the MCP system message

            if not mcp_url or not mcp_token:
                mcp_info_content = "MCP_CONFIG_ERROR: MCP_SERVER_URL or MCP_TEST_TOKEN is not configured."
            else:
                try:
                    # print(f"Attempting to connect to MCP server at {mcp_url} for /test_data") # Debug
                    mcp_connection = MCPConnection(server_url=mcp_url, token=mcp_token)
                    data = mcp_connection.get_data("test_data")
                    mcp_info_content = f"MCP_DATA_FETCHED: Successfully retrieved /test_data. Content: {data}"
                except HTTPError as e:
                    mcp_info_content = f"MCP_DATA_ERROR: Failed to retrieve /test_data. Status: {e.response.status_code}, Response: {e.response.text}"
                except Exception as e: # Catch other potential errors like ConnectionError
                    mcp_info_content = f"MCP_DATA_ERROR: Failed to retrieve /test_data. Error: {str(e)}"
            
            if mcp_info_content:
                # Add the MCP info as a system message. It will be part of the input to the LLM.
                provisional_messages.append({"role": "system", "content": mcp_info_content})

    # Now, prepare current_messages using provisional_messages for LiteLLM
    # This ensures SYSTEM_PROMPT is correctly placed if not already present.
    current_messages: List[Dict[str, str]]
    if not provisional_messages or provisional_messages[0]["role"] != "system":
        current_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + provisional_messages
    else:
        # If provisional_messages already starts with a system prompt, assume it's the main one.
        current_messages = provisional_messages

    # litellm is model-agnostic; we only need to supply the model name and key.
    completion = litellm.completion(
        model=MODEL_NAME,
        messages=current_messages, # Pass the (potentially modified) full history
    )

    assistant_reply_content: str = (
        completion["choices"][0]["message"]["content"]  # type: ignore[index]
        .strip()
    )
    
    # Append assistant's response to the history that was sent to LLM
    updated_messages = current_messages + [{"role": "assistant", "content": assistant_reply_content}]
    return updated_messages 