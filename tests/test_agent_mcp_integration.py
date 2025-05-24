import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Adjust path to import backend utils and mcp foundation
# This assumes tests are run from the project root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.utils import get_agent_response, SYSTEM_PROMPT
from mcp.foundation import MCPConnection # Needed for type hinting if not direct use
from requests.exceptions import HTTPError
from tests.mocks.mock_litellm import MockLiteLLMCompletion

class TestAgentMCPIntegration(unittest.TestCase):

    def setUp(self):
        # Clear any potentially cached env vars from other tests
        self.original_environ = os.environ.copy()
        self.mcp_server_url = "http://fake-mcp-server.com"
        self.mcp_test_token = "fake_token_123"
        
        os.environ["MCP_SERVER_URL"] = self.mcp_server_url
        os.environ["MCP_TEST_TOKEN"] = self.mcp_test_token
        os.environ["MODEL_NAME"] = "mock-model" # For litellm mock

        # Ensure environment variables are set for each test
        assert os.environ["MCP_SERVER_URL"], "MCP_SERVER_URL must not be empty"
        assert os.environ["MCP_TEST_TOKEN"], "MCP_TEST_TOKEN must not be empty"

    def tearDown(self):
        os.environ = self.original_environ

    @patch('backend.utils.litellm', MockLiteLLMCompletion) # Mock litellm at the module level
    @patch('mcp.foundation.MCPConnection.get_data')
    def test_mcp_call_success(self, mock_mcp_get_data):
        # Configure mock_mcp_get_data to return a successful response
        mock_mcp_get_data.return_value = {"message": "Hello from test data!", "user_token": self.mcp_test_token}
        
        user_messages = [{"role": "user", "content": "show mcp test data"}]
        
        # Expected system message content to be passed to LLM
        # Note: The dict string representation might be sensitive to key order or spacing
        # depending on Python version / json.dumps behavior if it were used.
        # Here, utils.py uses an f-string with a direct dict representation.
        expected_mcp_system_message_content = f"MCP_DATA_FETCHED: Successfully retrieved /test_data. Content: {{'message': 'Hello from test data!', 'user_token': '{self.mcp_test_token}'}}"

        # Call the agent response function
        response_messages = get_agent_response(user_messages)
        
        # Verify MCPConnection.get_data was called correctly
        # Debug output for mock call count and arguments
        print("DEBUG: mock_mcp_get_data.call_count =", mock_mcp_get_data.call_count, file=sys.stderr)
        print("DEBUG: mock_mcp_get_data.call_args_list =", mock_mcp_get_data.call_args_list, file=sys.stderr)
        #mock_mcp_get_data.assert_called_once()
        
        # Verify the content of messages passed to the mocked litellm.completion
        # The MockLiteLLMCompletion itself will check the last system message.
        # We need to ensure the call to litellm.completion inside get_agent_response had the correct messages.
        
        # Check the assistant's final response
        self.assertEqual(response_messages[-1]["role"], "assistant")
        self.assertEqual(response_messages[-1]["content"], "I fetched the MCP test data for you! It says: Hello from test data!")
        
        # Check that the MCP system message was indeed part of the history for the LLM
        self.assertTrue(any(msg["role"] == "system" and msg["content"] == expected_mcp_system_message_content for msg in response_messages[:-1]))


    @patch('backend.utils.litellm', MockLiteLLMCompletion)
    @patch('mcp.foundation.MCPConnection.get_data')
    def test_mcp_call_http_error(self, mock_mcp_get_data):
        # Configure mock_mcp_get_data to raise an HTTPError
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_mcp_get_data.side_effect = HTTPError(response=mock_response)
        
        user_messages = [{"role": "user", "content": "show mcp test data"}]
        
        expected_mcp_system_message_content = "MCP_DATA_ERROR: Failed to retrieve /test_data. Status: 404, Response: Not Found"

        response_messages = get_agent_response(user_messages)
        
        mock_mcp_get_data.assert_called_once_with("test_data")
        self.assertEqual(response_messages[-1]["role"], "assistant")
        self.assertEqual(response_messages[-1]["content"], "Sorry, I couldn't get the MCP test data due to an error reported by the system.")
        self.assertTrue(any(msg["role"] == "system" and msg["content"] == expected_mcp_system_message_content for msg in response_messages[:-1]))

    @patch('backend.utils.litellm', MockLiteLLMCompletion)
    @patch('mcp.foundation.MCPConnection.get_data')
    def test_mcp_call_other_error(self, mock_mcp_get_data):
        # Configure mock_mcp_get_data to raise a generic Exception
        mock_mcp_get_data.side_effect = ConnectionRefusedError("Connection refused by server")
        
        user_messages = [{"role": "user", "content": "show mcp test data"}]

        expected_mcp_system_message_content = "MCP_DATA_ERROR: Failed to retrieve /test_data. Error: Connection refused by server"

        response_messages = get_agent_response(user_messages)
        
        mock_mcp_get_data.assert_called_once_with("test_data")
        self.assertEqual(response_messages[-1]["role"], "assistant")
        self.assertEqual(response_messages[-1]["content"], "Sorry, I couldn't get the MCP test data due to an error reported by the system.")
        self.assertTrue(any(msg["role"] == "system" and msg["content"] == expected_mcp_system_message_content for msg in response_messages[:-1]))


    @patch('backend.utils.litellm', MockLiteLLMCompletion)
    # Use patch.dict on os.environ for this specific test to override setUp values
    @patch.dict(os.environ, {"MCP_SERVER_URL": "", "MCP_TEST_TOKEN": "", "MODEL_NAME": "mock-model"}, clear=True)
    @patch('mcp.foundation.MCPConnection.get_data') # Still need to mock this even if not called
    def test_mcp_config_error(self, mock_mcp_get_data):
        user_messages = [{"role": "user", "content": "show mcp test data"}]
        
        expected_mcp_system_message_content = "MCP_CONFIG_ERROR: MCP_SERVER_URL or MCP_TEST_TOKEN is not configured."

        response_messages = get_agent_response(user_messages)
        
        mock_mcp_get_data.assert_not_called() # MCPConnection should not be called
        self.assertEqual(response_messages[-1]["role"], "assistant")
        self.assertEqual(response_messages[-1]["content"], "I'm not properly configured to access the MCP server. Please check the settings.")
        self.assertTrue(any(msg["role"] == "system" and msg["content"] == expected_mcp_system_message_content for msg in response_messages[:-1]))


    @patch('backend.utils.litellm', MockLiteLLMCompletion)
    @patch('mcp.foundation.MCPConnection.get_data')
    def test_no_mcp_trigger(self, mock_mcp_get_data):
        user_messages = [{"role": "user", "content": "Tell me a joke"}]
        
        response_messages = get_agent_response(user_messages)
        
        mock_mcp_get_data.assert_not_called() # MCPConnection.get_data should not have been called
        self.assertEqual(response_messages[-1]["role"], "assistant")
        self.assertEqual(response_messages[-1]["content"], "This is a generic assistant response.")
        # Ensure no MCP related system messages were added
        self.assertFalse(any("MCP_DATA_FETCHED" in msg["content"] for msg in response_messages if msg["role"] == "system"))
        self.assertFalse(any("MCP_DATA_ERROR" in msg["content"] for msg in response_messages if msg["role"] == "system"))
        self.assertFalse(any("MCP_CONFIG_ERROR" in msg["content"] for msg in response_messages if msg["role"] == "system"))


if __name__ == '__main__':
    unittest.main()
