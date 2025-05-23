import unittest
from fastapi.testclient import TestClient
from mcp.test_server import app, TEST_TOKEN, TestDataModel

class TestMCPServer(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.valid_auth_header = {"Authorization": f"Bearer {TEST_TOKEN}"}
        self.invalid_auth_header = {"Authorization": "Bearer invalidtoken"}

    # Tests for GET /test_data
    def test_get_test_data_valid_token(self):
        response = self.client.get("/test_data", headers=self.valid_auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello from test data!", "user_token": TEST_TOKEN})

    def test_get_test_data_invalid_token(self):
        response = self.client.get("/test_data", headers=self.invalid_auth_header)
        # The current server implementation returns 403 for invalid token
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get("detail"), "Invalid or expired token")


    def test_get_test_data_no_token(self):
        response = self.client.get("/test_data")
        # The current server implementation returns 401 for no token
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json().get("detail"), "Not authenticated")


    # Tests for POST /submit_data
    def test_post_submit_data_valid_token_valid_payload(self):
        payload = {"some_value": "test input"}
        response = self.client.post("/submit_data", json=payload, headers=self.valid_auth_header)
        self.assertEqual(response.status_code, 200) # FastAPI default is 200 for POST
        self.assertEqual(response.json(), {"message": "Data submitted successfully!", "received_data": payload})

    def test_post_submit_data_invalid_token(self):
        payload = {"some_value": "test input"}
        response = self.client.post("/submit_data", json=payload, headers=self.invalid_auth_header)
        self.assertEqual(response.status_code, 403) # For invalid token
        self.assertEqual(response.json().get("detail"), "Invalid or expired token")

    def test_post_submit_data_no_token(self):
        payload = {"some_value": "test input"}
        response = self.client.post("/submit_data", json=payload)
        self.assertEqual(response.status_code, 401) # For no token
        self.assertEqual(response.json().get("detail"), "Not authenticated")


    def test_post_submit_data_valid_token_invalid_payload(self):
        # Pydantic model TestDataModel expects 'some_value'
        invalid_payload = {"wrong_key": "test input"}
        response = self.client.post("/submit_data", json=invalid_payload, headers=self.valid_auth_header)
        self.assertEqual(response.status_code, 422) # Unprocessable Entity for Pydantic validation error
        # You can also check the detail of the validation error if needed
        # For example: self.assertTrue("field required" in response.json()["detail"][0]["msg"].lower())

if __name__ == '__main__':
    unittest.main()
