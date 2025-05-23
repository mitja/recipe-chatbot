import requests
import sys
import time

# Configuration
MAIN_APP_URL = "http://localhost:8000/"
MCP_SERVER_BASE_URL = "http://localhost:8001"
MCP_TEST_DATA_ENDPOINT = "/test_data"
MCP_VALID_TOKEN = "test_token_123"  # Should match TEST_TOKEN in mcp/test_server.py
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds

def print_status(message, success):
    status_icon = "✅" if success else "❌"
    print(f"{status_icon} {message}")

def attempt_request(method, url, headers=None, expected_status=200, check_json_contains=None, check_text_contains=None):
    for i in range(MAX_RETRIES):
        try:
            response = requests.request(method, url, headers=headers, timeout=10)
            if response.status_code == expected_status:
                if check_json_contains:
                    json_response = response.json()
                    if all(item in json_response.items() for item in check_json_contains.items()):
                        return True, response
                elif check_text_contains:
                    if check_text_contains in response.text:
                        return True, response
                elif not check_json_contains and not check_text_contains : # Only status check
                    return True, response
            # If status is not as expected but it's the last retry, return False with the actual response
            if i == MAX_RETRIES - 1:
                return False, response
        except requests.ConnectionError:
            if i == MAX_RETRIES - 1:
                return False, None # No response if connection error on last attempt
        except requests.Timeout:
            if i == MAX_RETRIES - 1:
                return False, None # No response if timeout on last attempt
        
        print(f"  Attempt {i+1}/{MAX_RETRIES} failed. Retrying in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
    return False, None # Should be unreachable if MAX_RETRIES > 0

def check_main_app():
    print("\n--- Checking Main Application (Recipe Chatbot) ---")
    success, response = attempt_request(
        "GET", 
        MAIN_APP_URL, 
        expected_status=200, 
        check_text_contains="<title>Recipe Chatbot</title>"
    )
    if success:
        print_status(f"Main App ({MAIN_APP_URL}) is UP and serving expected content.", True)
        return True
    else:
        status_code = response.status_code if response else "N/A (Connection Error/Timeout)"
        print_status(f"Main App ({MAIN_APP_URL}) check FAILED. Status: {status_code}", False)
        return False

def check_mcp_server():
    print("\n--- Checking MCP Test Server ---")
    mcp_server_ok = True
    mcp_test_data_url = MCP_SERVER_BASE_URL + MCP_TEST_DATA_ENDPOINT

    # 1. Test MCP Server reachability (unauthenticated)
    print(f"Attempting GET {mcp_test_data_url} (expecting 401/403 for auth error)...")
    # Test for either 401 or 403 as the exact code might vary slightly by framework/config for missing/bad token
    unauth_success_401, _ = attempt_request("GET", mcp_test_data_url, expected_status=401)
    unauth_success_403, response_403 = attempt_request("GET", mcp_test_data_url, expected_status=403)


    if unauth_success_401:
        print_status(f"MCP Server ({mcp_test_data_url}) correctly requires authentication (got 401).", True)
    elif unauth_success_403:
        print_status(f"MCP Server ({mcp_test_data_url}) correctly requires authentication (got 403).", True)
    else:
        # Provide more info if available
        status_code_401 = _.status_code if _ and hasattr(_, 'status_code') else "N/A"
        status_code_403 = response_403.status_code if response_403 and hasattr(response_403, 'status_code') else "N/A"
        print_status(f"MCP Server ({mcp_test_data_url}) did NOT return 401 (actual: {status_code_401}) or 403 (actual: {status_code_403}) for unauthenticated request.", False)
        mcp_server_ok = False

    # 2. Test MCP Server with valid token
    print(f"\nAttempting GET {mcp_test_data_url} with VALID token...")
    headers = {"Authorization": f"Bearer {MCP_VALID_TOKEN}"}
    auth_success, response = attempt_request(
        "GET",
        mcp_test_data_url,
        headers=headers,
        expected_status=200,
        check_json_contains={"message": "Hello from test data!"} # Check a key part of the expected JSON
    )

    if auth_success:
        print_status(f"MCP Server ({mcp_test_data_url}) responded correctly to authenticated request.", True)
    else:
        status_code = response.status_code if response else "N/A (Connection Error/Timeout)"
        print_status(f"MCP Server ({mcp_test_data_url}) FAILED authenticated request. Status: {status_code}", False)
        mcp_server_ok = False
        if response and response.status_code == 200: # It was 200, but content didn't match
             print(f"  Response JSON: {response.json()}")


    return mcp_server_ok

if __name__ == "__main__":
    print("Starting Docker Compose Smoke Test...")
    # Give services a moment to start up, especially if run immediately after docker-compose up
    # time.sleep(10) # Optional: Initial delay 

    main_app_healthy = check_main_app()
    mcp_server_healthy = check_mcp_server()

    if main_app_healthy and mcp_server_healthy:
        print("\n✅ Smoke test PASSED! Both services are responsive and basic checks are successful.")
        sys.exit(0)
    else:
        print("\n❌ Smoke test FAILED. Please check the output above for details.")
        sys.exit(1)
