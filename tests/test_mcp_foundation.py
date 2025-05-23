import unittest
from unittest.mock import patch, MagicMock
from mcp.foundation import MCPConnection
from requests.exceptions import HTTPError

class TestMCPConnection(unittest.TestCase):

    def setUp(self):
        self.server_url = "http://testserver.com"
        self.token = "test_token"
        self.conn = MCPConnection(self.server_url, self.token)

    def test_init(self):
        """Test that server_url and token are stored correctly."""
        self.assertEqual(self.conn.server_url, self.server_url)
        self.assertEqual(self.conn.token, self.token)

    @patch('mcp.foundation.requests.get')
    def test_get_data_success(self, mock_get):
        """Test successful GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        expected_data = {"key": "value"}
        mock_response.json.return_value = expected_data
        mock_get.return_value = mock_response

        endpoint = "test_endpoint"
        data = self.conn.get_data(endpoint)

        full_url = f"{self.server_url}/{endpoint}"
        expected_headers = {"Authorization": f"Bearer {self.token}"}
        mock_get.assert_called_once_with(full_url, headers=expected_headers)
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(data, expected_data)

    @patch('mcp.foundation.requests.get')
    def test_get_data_failure(self, mock_get):
        """Test failed GET request (e.g., 401 Unauthorized)."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        # Configure raise_for_status to raise HTTPError for 4xx/5xx codes
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        endpoint = "test_endpoint"
        with self.assertRaises(HTTPError):
            self.conn.get_data(endpoint)

        full_url = f"{self.server_url}/{endpoint}"
        expected_headers = {"Authorization": f"Bearer {self.token}"}
        mock_get.assert_called_once_with(full_url, headers=expected_headers)
        mock_response.raise_for_status.assert_called_once()

    @patch('mcp.foundation.requests.post')
    def test_post_data_success(self, mock_post):
        """Test successful POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        expected_response_data = {"result": "success"}
        mock_response.json.return_value = expected_response_data
        mock_post.return_value = mock_response

        endpoint = "submit_endpoint"
        payload = {"data_key": "data_value"}
        response_data = self.conn.post_data(endpoint, payload)

        full_url = f"{self.server_url}/{endpoint}"
        expected_headers = {"Authorization": f"Bearer {self.token}"}
        mock_post.assert_called_once_with(full_url, headers=expected_headers, json=payload)
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(response_data, expected_response_data)

    @patch('mcp.foundation.requests.post')
    def test_post_data_failure(self, mock_post):
        """Test failed POST request (e.g., 403 Forbidden)."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        # Configure raise_for_status to raise HTTPError for 4xx/5xx codes
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_post.return_value = mock_response

        endpoint = "submit_endpoint"
        payload = {"data_key": "data_value"}
        with self.assertRaises(HTTPError):
            self.conn.post_data(endpoint, payload)

        full_url = f"{self.server_url}/{endpoint}"
        expected_headers = {"Authorization": f"Bearer {self.token}"}
        mock_post.assert_called_once_with(full_url, headers=expected_headers, json=payload)
        mock_response.raise_for_status.assert_called_once()

if __name__ == '__main__':
    unittest.main()
