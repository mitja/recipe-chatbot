import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys
import json

# Adjust path to import from the root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.utils import get_agent_response, SYSTEM_PROMPT
from backend.tool_definitions import TOOL_DEFINITIONS # For verification
# Assuming execute_tool is in backend.tool_executor
# from backend.tool_executor import execute_tool # We will mock this directly

# Mock for the database session if needed by execute_tool, though execute_tool itself will be mocked
class MockDbSession:
    def close(self):
        pass

# Mock for get_db generator
def mock_get_db():
    yield MockDbSession()
    # No actual db operations, so simple mock session is enough if execute_tool is well-mocked

class TestAgentFunctionCalling(unittest.TestCase):

    def setUp(self):
        self.original_environ = os.environ.copy()
        os.environ["MODEL_NAME"] = "mock-model-for-function-calling"
        # Any other env vars needed by backend.utils can be set here

        # Reset TOOL_DEFINITIONS to a known state for tests if it could be modified elsewhere (unlikely for constants)
        # from backend.tool_definitions import TOOL_DEFINITIONS as ACTUAL_TOOL_DEFS
        # self.TOOL_DEFS_FOR_TEST = [t.copy() for t in ACTUAL_TOOL_DEFS] # Deepcopy if complex

    def tearDown(self):
        os.environ = self.original_environ

    @patch('backend.utils.execute_tool')
    @patch('backend.utils.litellm.completion')
    @patch('backend.utils.get_db', new=mock_get_db) # Mock get_db
    def test_function_call_create_family_successful(self, mock_litellm_completion, mock_execute_tool):
        # --- First LLM call: Simulate LLM requesting 'create_family' tool ---
        first_llm_response_message_content = {
            "role": "assistant",
            "content": None, # Standard for tool use
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "create_family",
                        "arguments": json.dumps({"name": "The Simpsons", "slug": "simpsons"})
                    }
                }
            ]
        }
        # LiteLLM's completion message object structure might be slightly different,
        # ensure it matches what's expected (e.g. a Pydantic model with model_dump())
        # For testing, we can create a MagicMock that has the structure.
        mock_first_completion_choice_message = MagicMock()
        mock_first_completion_choice_message.role = "assistant"
        mock_first_completion_choice_message.content = None
        mock_first_completion_choice_message.tool_calls = [MagicMock()]
        mock_first_completion_choice_message.tool_calls[0].id = "call_123"
        mock_first_completion_choice_message.tool_calls[0].type = "function"
        mock_first_completion_choice_message.tool_calls[0].function.name = "create_family"
        mock_first_completion_choice_message.tool_calls[0].function.arguments = json.dumps({"name": "The Simpsons", "slug": "simpsons"})

        # .model_dump() is called on this object in get_agent_response
        mock_first_completion_choice_message.model_dump.return_value = first_llm_response_message_content


        # --- Tool execution result ---
        mock_execute_tool.return_value = "Successfully created family: The Simpsons (ID: 1)"

        # --- Second LLM call: Simulate LLM generating final response ---
        second_llm_response_message_content = {
            "role": "assistant",
            "content": "Okay, I've created the family 'The Simpsons' for you."
        }
        mock_second_completion_choice_message = MagicMock()
        mock_second_completion_choice_message.role = "assistant"
        mock_second_completion_choice_message.content = "Okay, I've created the family 'The Simpsons' for you."
        mock_second_completion_choice_message.tool_calls = None # No further tool calls
        mock_second_completion_choice_message.model_dump.return_value = second_llm_response_message_content


        # Configure the mock for litellm.completion to return these responses in order
        mock_litellm_completion.side_effect = [
            MagicMock(choices=[MagicMock(message=mock_first_completion_choice_message)]), # Mock for 1st call
            MagicMock(choices=[MagicMock(message=mock_second_completion_choice_message)]) # Mock for 2nd call
        ]

        # --- Call get_agent_response ---
        user_messages = [{"role": "user", "content": "Please create a family called The Simpsons with slug simpsons."}]
        final_history = get_agent_response(user_messages)

        # --- Assertions ---
        # 1. Check litellm.completion calls
        self.assertEqual(mock_litellm_completion.call_count, 2)

        # Call 1 args
        call1_args, call1_kwargs = mock_litellm_completion.call_args_list[0]
        self.assertEqual(call1_kwargs['model'], os.environ["MODEL_NAME"])
        self.assertEqual(call1_kwargs['messages'][0]['role'], "system") # SYSTEM_PROMPT
        self.assertEqual(call1_kwargs['messages'][1]['role'], "user")
        self.assertEqual(call1_kwargs['messages'][1]['content'], user_messages[0]['content'])
        self.assertEqual(call1_kwargs['tools'], TOOL_DEFINITIONS)
        self.assertEqual(call1_kwargs['tool_choice'], "auto")

        # Call 2 args
        call2_args, call2_kwargs = mock_litellm_completion.call_args_list[1]
        self.assertEqual(call2_kwargs['model'], os.environ["MODEL_NAME"])
        expected_messages_for_call2 = [
            {"role": "system", "content": SYSTEM_PROMPT},
            user_messages[0],
            first_llm_response_message_content, # LLM's first response (tool call request)
            { # Tool execution result
                "role": "tool",
                "tool_call_id": "call_123",
                "name": "create_family",
                "content": "Successfully created family: The Simpsons (ID: 1)"
            }
        ]
        self.assertEqual(call2_kwargs['messages'], expected_messages_for_call2)
        # Ensure 'tools' and 'tool_choice' are NOT in kwargs for 2nd call (or are None)
        self.assertNotIn('tools', call2_kwargs)
        self.assertNotIn('tool_choice', call2_kwargs)


        # 2. Check execute_tool call
        mock_execute_tool.assert_called_once_with(
            tool_name="create_family",
            tool_args={"name": "The Simpsons", "slug": "simpsons"},
            db=unittest.mock.ANY # Check that a session object was passed
        )

        # 3. Check final history returned by get_agent_response
        self.assertEqual(len(final_history), 5) # System, User, Assistant (tool call), Tool, Assistant (final)
        self.assertEqual(final_history[0]['role'], "system")
        self.assertEqual(final_history[1]['role'], "user")
        self.assertEqual(final_history[2]['role'], "assistant") # LLM's request for tool call
        self.assertTrue(final_history[2]['tool_calls'] is not None)
        self.assertEqual(final_history[3]['role'], "tool")     # Tool execution result
        self.assertEqual(final_history[4]['role'], "assistant") # Final LLM response
        self.assertEqual(final_history[4]['content'], "Okay, I've created the family 'The Simpsons' for you.")


    @patch('backend.utils.execute_tool')
    @patch('backend.utils.litellm.completion')
    @patch('backend.utils.get_db', new=mock_get_db)
    def test_no_function_call_direct_response(self, mock_litellm_completion, mock_execute_tool):
        # --- First LLM call: Simulate LLM responding directly without tool ---
        direct_response_message_content = {
            "role": "assistant",
            "content": "I cannot help you with that specific request right now."
        }
        mock_direct_response_message = MagicMock()
        mock_direct_response_message.role = "assistant"
        mock_direct_response_message.content = "I cannot help you with that specific request right now."
        mock_direct_response_message.tool_calls = None # Crucially, no tool_calls
        mock_direct_response_message.model_dump.return_value = direct_response_message_content


        mock_litellm_completion.return_value = MagicMock(choices=[MagicMock(message=mock_direct_response_message)])

        # --- Call get_agent_response ---
        user_messages = [{"role": "user", "content": "Tell me something not tool related."}]
        final_history = get_agent_response(user_messages)

        # --- Assertions ---
        # 1. Check litellm.completion was called only once
        mock_litellm_completion.assert_called_once()
        call_args, call_kwargs = mock_litellm_completion.call_args_list[0]
        self.assertEqual(call_kwargs['tools'], TOOL_DEFINITIONS) # Tools are offered
        self.assertEqual(call_kwargs['tool_choice'], "auto")

        # 2. Check execute_tool was NOT called
        mock_execute_tool.assert_not_called()

        # 3. Check final history
        self.assertEqual(len(final_history), 3) # System, User, Assistant (direct response)
        self.assertEqual(final_history[2]['role'], "assistant")
        self.assertEqual(final_history[2]['content'], "I cannot help you with that specific request right now.")

    @patch('backend.utils.execute_tool')
    @patch('backend.utils.litellm.completion')
    @patch('backend.utils.get_db', new=mock_get_db)
    def test_function_call_json_decode_error_in_args(self, mock_litellm_completion, mock_execute_tool):
        # --- First LLM call: Simulate LLM requesting tool with bad JSON args ---
        bad_json_args = "{\"name\": \"The Simpsons\", \"slug\": simpsons}" # 'simpsons' not quoted

        mock_first_completion_choice_message = MagicMock()
        mock_first_completion_choice_message.role = "assistant"
        mock_first_completion_choice_message.content = None
        mock_first_completion_choice_message.tool_calls = [MagicMock()]
        mock_first_completion_choice_message.tool_calls[0].id = "call_err_123"
        mock_first_completion_choice_message.tool_calls[0].type = "function"
        mock_first_completion_choice_message.tool_calls[0].function.name = "create_family"
        mock_first_completion_choice_message.tool_calls[0].function.arguments = bad_json_args
        mock_first_completion_choice_message.model_dump.return_value = { # Construct dict for history
             "role": "assistant", "content": None,
             "tool_calls": [{
                 "id": "call_err_123", "type": "function",
                 "function": {"name": "create_family", "arguments": bad_json_args}
             }]
        }

        # --- Second LLM call: Simulate LLM generating final response after error ---
        error_response_content = "It seems there was an issue with the arguments for the tool."
        mock_second_completion_choice_message = MagicMock()
        mock_second_completion_choice_message.role = "assistant"
        mock_second_completion_choice_message.content = error_response_content
        mock_second_completion_choice_message.tool_calls = None
        mock_second_completion_choice_message.model_dump.return_value = {
            "role": "assistant", "content": error_response_content
        }

        mock_litellm_completion.side_effect = [
            MagicMock(choices=[MagicMock(message=mock_first_completion_choice_message)]),
            MagicMock(choices=[MagicMock(message=mock_second_completion_choice_message)])
        ]

        user_messages = [{"role": "user", "content": "Create family with bad args."}]
        final_history = get_agent_response(user_messages)

        # Assertions
        self.assertEqual(mock_litellm_completion.call_count, 2)
        mock_execute_tool.assert_not_called() # execute_tool should not be called due to JSON error

        self.assertEqual(final_history[3]['role'], "tool")
        self.assertEqual(final_history[3]['tool_call_id'], "call_err_123")
        self.assertTrue("Error: Invalid JSON arguments provided for create_family." in final_history[3]['content'])
        self.assertEqual(final_history[4]['content'], error_response_content)


if __name__ == '__main__':
    unittest.main()
