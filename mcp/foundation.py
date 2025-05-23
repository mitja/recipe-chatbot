import requests
from requests.exceptions import HTTPError

class MCPConnection:
    """Handles connection and data exchange with an MCP server."""

    def __init__(self, server_url: str, token: str):
        """
        Initializes the MCPConnection.

        Args:
            server_url: The base URL of the MCP server.
            token: The authentication token.
        """
        self.server_url = server_url
        self.token = token

    def get_data(self, endpoint: str) -> dict:
        """
        Retrieves data from the specified endpoint.

        Args:
            endpoint: The API endpoint to query.

        Returns:
            A dictionary containing the JSON response from the server.

        Raises:
            HTTPError: If the server returns an error status code.
        """
        full_url = f"{self.server_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx status codes
        return response.json()

    def post_data(self, endpoint: str, payload: dict) -> dict:
        """
        Sends data to the specified endpoint.

        Args:
            endpoint: The API endpoint to send data to.
            payload: A dictionary containing the data to send.

        Returns:
            A dictionary containing the JSON response from the server.

        Raises:
            HTTPError: If the server returns an error status code.
        """
        full_url = f"{self.server_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(full_url, headers=headers, json=payload)
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx status codes
        return response.json()
