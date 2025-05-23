from mcp.foundation import MCPConnection
from requests.exceptions import HTTPError

SERVER_URL = "http://127.0.0.1:8000"
VALID_TOKEN = "test_token_123"  # Same as TEST_TOKEN in test_server.py
INVALID_TOKEN = "wrong_token"

if __name__ == "__main__":
    print("--- Test Client for MCPConnection ---")

    # 1. Test with VALID_TOKEN
    print(f"\nInitializing MCPConnection with VALID_TOKEN ({VALID_TOKEN})...")
    conn_valid = MCPConnection(server_url=SERVER_URL, token=VALID_TOKEN)

    # a. Attempt GET /test_data with valid token
    print("\nAttempting GET /test_data with valid token...")
    try:
        response = conn_valid.get_data("test_data")
        print(f"Response: {response}")
    except HTTPError as e:
        print(f"Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # b. Attempt POST /submit_data with valid token
    print("\nAttempting POST /submit_data with valid token...")
    sample_payload = {"some_value": "Hello server"}
    try:
        response = conn_valid.post_data("submit_data", payload=sample_payload)
        print(f"Response: {response}")
    except HTTPError as e:
        print(f"Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # 2. Test with INVALID_TOKEN
    print(f"\nInitializing MCPConnection with INVALID_TOKEN ({INVALID_TOKEN})...")
    conn_invalid = MCPConnection(server_url=SERVER_URL, token=INVALID_TOKEN)

    # c. Attempt GET /test_data with invalid token
    print("\nAttempting GET /test_data with invalid token...")
    try:
        response = conn_invalid.get_data("test_data")
        print(f"Response: {response}") # Should not reach here
    except HTTPError as e:
        if e.response.status_code == 403:
            print(f"Successfully caught expected authentication error: {e.response.status_code} - {e.response.json().get('detail')}")
        else:
            print(f"Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # d. Attempt POST /submit_data with invalid token
    print("\nAttempting POST /submit_data with invalid token...")
    try:
        response = conn_invalid.post_data("submit_data", payload=sample_payload)
        print(f"Response: {response}") # Should not reach here
    except HTTPError as e:
        if e.response.status_code == 403:
            print(f"Successfully caught expected authentication error: {e.response.status_code} - {e.response.json().get('detail')}")
        else:
            print(f"Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("\n--- Test Client Finished ---")
