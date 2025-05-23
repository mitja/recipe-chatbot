import json

class MockLiteLLMCompletion:
    @staticmethod
    def completion(model, messages, **kwargs):
        # Default response for generic messages
        response_content = "This is a generic assistant response."
        
        # Check the last system message for MCP specific content
        # The MCP info message is appended, so it might be the last one
        # if the trigger phrase was the user's last message.
        # However, the main system prompt is prepended if not present, 
        # so we should iterate to find the relevant MCP system message.
        mcp_system_message = None
        for msg in reversed(messages):
            if msg["role"] == "system":
                if "MCP_DATA_FETCHED:" in msg["content"] or \
                   "MCP_DATA_ERROR:" in msg["content"] or \
                   "MCP_CONFIG_ERROR:" in msg["content"]:
                    mcp_system_message = msg["content"]
                    break
        
        if mcp_system_message:
            system_message_content = mcp_system_message
            if "MCP_DATA_FETCHED:" in system_message_content:
                try:
                    # Extract the JSON part of the content string
                    # Example: "MCP_DATA_FETCHED: Successfully retrieved /test_data. Content: {'message': 'Hello from test data!', 'user_token': 'test_token_123'}"
                    content_str_part = system_message_content.split("Content: ", 1)[1]
                    
                    # Simple check for the expected content from mcp.test_server
                    if "'message': 'Hello from test data!'" in content_str_part and \
                       "'user_token': 'test_token_123'" in content_str_part:
                        response_content = "I fetched the MCP test data for you! It says: Hello from test data!"
                    else:
                        response_content = "I fetched some MCP data, but it looks different than expected."

                except Exception as e:
                    response_content = f"I tried to parse MCP data but encountered an error: {str(e)}"

            elif "MCP_DATA_ERROR:" in system_message_content:
                response_content = "Sorry, I couldn't get the MCP test data due to an error reported by the system."
            elif "MCP_CONFIG_ERROR:" in system_message_content:
                response_content = "I'm not properly configured to access the MCP server. Please check the settings."

        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": response_content
                }
            }]
        }
