from __future__ import annotations

"""Utility helpers for the recipe chatbot backend.

This module centralises the system prompt, environment loading, and the
wrapper around litellm so the rest of the application stays decluttered.
"""

import os
from pathlib import Path
from typing import Final, List, Dict

import litellm  # type: ignore
import json # For parsing function arguments from LLM
from dotenv import load_dotenv

from mcp.foundation import MCPConnection
from requests.exceptions import HTTPError
from backend.tool_definitions import TOOL_DEFINITIONS
from backend.tool_executor import execute_tool # Added
from database.database_config import get_db # Added

# Ensure the .env file is loaded as early as possible.
load_dotenv(override=False)

# --- Constants -------------------------------------------------------------------

_DEFAULT_SYSTEM_PROMPT: str = (
    "You are an expert chef recommending delicious and useful recipes. "
    "You can also help manage family information and shopping lists using available tools when appropriate. " # Added this sentence
    "Present only one recipe at a time. If the user doesn't specify what ingredients "
    "they have available, assume only basic ingredients are available."
    "Be descriptive in the steps of the recipe, so it is easy to follow."
    "Have variety in your recipes, don't just recommend the same thing over and over."
    "You MUST suggest a complete recipe; don't ask follow-up questions."
    "Mention the serving size in the recipe. If not specified, assume 2 people."
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
    # --- Start of new function calling logic ---
    
    # Make a mutable copy of the incoming messages
    current_conversation_history = list(messages)

    # Ensure SYSTEM_PROMPT is at the beginning of the conversation if not already there
    if not current_conversation_history or current_conversation_history[0].get("role") != "system":
        current_conversation_history.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    elif current_conversation_history[0].get("role") == "system" and current_conversation_history[0].get("content") != SYSTEM_PROMPT:
        # If a system prompt is present but it's not our main one,
        # we might replace it or prepend ours. For now, let's assume if a system prompt
        # is there, it's either ours or one from a previous tool interaction that should be kept.
        # If the first message is a system message, we'll assume it's either the main one
        # or a tool-related one. If it's not the main one, this means the main one might be missing
        # if this is the start of a turn after tool use.
        # A simpler approach: always ensure the *first* message for the *first* LLM call in a turn is the main system prompt.
        # The provided logic below handles this: if current_conversation_history[0] is not system, it inserts.
        # If it IS system, it's assumed to be handled (either it's the main one, or it's a tool system message that should be there).
        # This seems fine for now, as the main system prompt guides overall behavior.
        pass

    # --- First LLM Call ---
    print(f"Debug: Sending to LiteLLM (1st call): {current_conversation_history}") # Debug
    print(f"Debug: Using tools: {TOOL_DEFINITIONS}") # Debug

    completion = litellm.completion(
        model=MODEL_NAME,
        messages=current_conversation_history,
        tools=TOOL_DEFINITIONS,
        tool_choice="auto"  # Let the LLM decide if it wants to use a tool
    )
    
    print(f"Debug: LiteLLM response (1st call): {completion}") # Debug

    # Get the first choice from the completion
    llm_response_message = completion.choices[0].message

    # Append the LLM's initial response (which might be a tool call request or a direct answer)
    current_conversation_history.append(llm_response_message.model_dump()) # Append as dict

    # --- Check for Tool Calls ---
    if llm_response_message.tool_calls:
        print(f"Debug: LLM requested tool calls: {llm_response_message.tool_calls}") # Debug
        
        db_session = next(get_db()) # Obtain a database session
        try:
            for tool_call in llm_response_message.tool_calls:
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    print(f"Error: Could not decode JSON arguments for tool {function_name}: {tool_call.function.arguments}") # Debug
                    tool_result_content = f"Error: Invalid JSON arguments provided for {function_name}."
                    # Potentially log the error and invalid arguments string
                else:
                    print(f"Debug: Executing tool '{function_name}' with args: {function_args}") # Debug
                    tool_result_content = execute_tool(
                        tool_name=function_name,
                        tool_args=function_args,
                        db=db_session
                    )
                
                print(f"Debug: Tool '{function_name}' result: {tool_result_content}") # Debug
                current_conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(tool_result_content) # Ensure content is a string
                })
        finally:
            db_session.close()

        # --- Second LLM Call (after processing tool calls) ---
        print(f"Debug: Sending to LiteLLM (2nd call): {current_conversation_history}") # Debug
        
        # The SYSTEM_PROMPT should already be at the start from the first call's preparation.
        # We don't pass `tools` or `tool_choice` here, as we expect a direct natural language response.
        final_completion = litellm.completion(
            model=MODEL_NAME,
            messages=current_conversation_history
        )
        print(f"Debug: LiteLLM response (2nd call): {final_completion}") # Debug
        
        final_llm_response_message = final_completion.choices[0].message
        current_conversation_history.append(final_llm_response_message.model_dump())
    
    # If no tool_calls, the llm_response_message from the first call is the final one.
    # The current_conversation_history already has it appended.
    
    return current_conversation_history # Return the full, updated conversation history