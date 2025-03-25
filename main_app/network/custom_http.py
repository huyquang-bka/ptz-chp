import requests
from PyQt5.QtCore import QSettings
from typing import Dict, Any, Optional, Tuple, Callable


class CustomHTTPRequest:
    """Class to handle HTTP requests to the API with token refresh capability"""

    def __init__(self, base_url: str = "https://api.example.com", additional_route: str = "/api",
                 refresh_token_endpoint: str = "/token/auth"):
        """Initialize the HTTP client

        Args:
            base_url (str): The base URL of the API
            additional_route (str): Additional route to append to the base URL
            refresh_token_endpoint (str): Endpoint for refreshing tokens
        """
        self.base_url = base_url
        self.additional_route = additional_route
        self.refresh_token_endpoint = refresh_token_endpoint

        # Create QSettings instance
        self.settings = QSettings("PTZ-CHP", "UserData")

        # Auth tokens
        self.access_token = None
        self.refresh_token = None
        self.token_type = "Bearer"

        # Load tokens if available
        self._load_tokens()

        # Refresh callback - can be set by the application
        self.on_token_refreshed = None
        self.on_refresh_failed = None

    def set_refresh_callback(self, success_callback: Callable = None, failure_callback: Callable = None):
        """Set callbacks for token refresh events

        Args:
            success_callback: Function to call when token refresh succeeds
            failure_callback: Function to call when token refresh fails
        """
        self.on_token_refreshed = success_callback
        self.on_refresh_failed = failure_callback

    def _load_tokens(self):
        """Load tokens from QSettings"""
        self.access_token = self.settings.value("access_token", None)
        self.refresh_token = self.settings.value("refresh_token", None)
        self.token_type = self.settings.value("token_type", "Bearer")

    def _save_tokens(self):
        """Save tokens to QSettings"""
        self.settings.setValue("access_token", self.access_token)
        self.settings.setValue("refresh_token", self.refresh_token)
        self.settings.setValue("token_type", self.token_type)
        self.settings.sync()  # Ensure settings are written to storage

    def set_tokens(self, access_token: str, refresh_token: str, token_type: str = "Bearer"):
        """Set authentication tokens

        Args:
            access_token (str): The access token
            refresh_token (str): The refresh token
            token_type (str): The token type (default: Bearer)
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self._save_tokens()

    def clear_tokens(self):
        """Clear authentication tokens"""
        self.access_token = None
        self.refresh_token = None
        self.token_type = "Bearer"

        # Remove from QSettings
        self.settings.remove("access_token")
        self.settings.remove("refresh_token")
        self.settings.remove("token_type")
        self.settings.sync()

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers

        Returns:
            Dict[str, str]: Headers with authorization token
        """
        if not self.access_token:
            return {}

        return {
            'Authorization': f"{self.token_type} {self.access_token}"
        }

    def refresh_token(self) -> bool:
        """Refresh the access token using the refresh token

        Returns:
            bool: True if refresh was successful, False otherwise
        """
        if not self.refresh_token:
            print("No refresh token available")
            return False

        try:
            # Prepare refresh payload
            payload = {
                'client_id': 'EPS',  # These should be loaded from config
                'client_secret': 'b0udcdl8k80cqiyt63uq',
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }

            # Make refresh request
            url = self.get_full_url(self.refresh_token_endpoint)
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                # Parse response
                data = response.json()
                self.access_token = data.get('access_token')
                # Some APIs return a new refresh token, others don't
                if 'refresh_token' in data:
                    self.refresh_token = data.get('refresh_token')
                self.token_type = data.get('token_type', self.token_type)

                # Save tokens
                self._save_tokens()

                # Call success callback if set
                if self.on_token_refreshed:
                    self.on_token_refreshed()

                return True
            else:
                print(
                    f"Token refresh failed: {response.status_code} - {response.text}")

                # Call failure callback if set
                if self.on_refresh_failed:
                    self.on_refresh_failed()

                return False
        except Exception as e:
            print(f"Token refresh error: {e}")

            # Call failure callback if set
            if self.on_refresh_failed:
                self.on_refresh_failed()

            return False

    def get_full_url(self, endpoint: str) -> str:
        """Get the full URL for an endpoint

        Args:
            endpoint (str): The API endpoint

        Returns:
            str: The full URL
        """
        # Make sure endpoint starts with a slash
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint

        return f"{self.base_url}{self.additional_route}{endpoint}"

    def _handle_response(self, response: requests.Response, retry_func, retry_count: int = 0) -> Tuple[requests.Response, bool]:
        """Handle API response and refresh token if needed

        Args:
            response: The API response
            retry_func: Function to retry the request
            retry_count: Number of retry attempts made

        Returns:
            Tuple[requests.Response, bool]: The response and whether it was retried
        """
        # If unauthorized and we haven't retried yet
        if response.status_code == 401 and retry_count < 1:
            print("Received 401 Unauthorized, attempting to refresh token")

            # Try to refresh the token
            if self.refresh_token():
                print("Token refreshed successfully, retrying request")
                # Retry the request with the new token
                return retry_func(retry_count + 1)
            else:
                print("Token refresh failed")

        return response, retry_count > 0

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None, payload: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = None, retry_count: int = 0) -> requests.Response:
        """Make a GET request to the API with automatic token refresh

        Args:
            endpoint (str): The API endpoint
            params (Dict[str, Any], optional): Query parameters
            headers (Dict[str, str], optional): Request headers
            payload (Dict[str, Any], optional): Request payload for GET with body
            timeout (Optional[int], optional): Request timeout
            retry_count (int): Number of retry attempts made

        Returns:
            requests.Response: The response from the API
        """
        # Merge auth headers with provided headers
        all_headers = self.get_auth_headers()
        if headers:
            all_headers.update(headers)

        url = self.get_full_url(endpoint)

        if payload:
            # Some APIs use GET with a request body
            response = requests.get(
                url, params=params, headers=all_headers, json=payload, timeout=timeout)
        else:
            response = requests.get(
                url, params=params, headers=all_headers, timeout=timeout)

        # Define retry function
        def retry(new_retry_count):
            return self.get(endpoint, params, headers, payload, timeout, new_retry_count)

        # Handle response and potential token refresh
        response, was_retried = self._handle_response(
            response, retry, retry_count)

        return response

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
             timeout: Optional[int] = None, retry_count: int = 0, file: Optional[bytes] = None) -> requests.Response:
        """Make a POST request to the API with automatic token refresh

        Args:
            endpoint (str): The API endpoint
            data (Dict[str, Any], optional): Form data
            json (Dict[str, Any], optional): JSON data
            headers (Dict[str, str], optional): Request headers
            timeout (Optional[int], optional): Request timeout
            retry_count (int): Number of retry attempts made

        Returns:
            requests.Response: The response from the API
        """
        # Merge auth headers with provided headers
        all_headers = self.get_auth_headers()
        if headers:
            all_headers.update(headers)

        url = self.get_full_url(endpoint)
        response = requests.post(
            url, data=data, json=json, headers=all_headers, timeout=timeout, files=file)

        # Define retry function
        def retry(new_retry_count):
            return self.post(endpoint, data, json, headers, timeout, new_retry_count, file)

        # Handle response and potential token refresh
        response, was_retried = self._handle_response(
            response, retry, retry_count)

        return response

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None, retry_count: int = 0) -> requests.Response:
        """Make a PUT request to the API with automatic token refresh

        Args:
            endpoint (str): The API endpoint
            data (Dict[str, Any], optional): Form data
            json (Dict[str, Any], optional): JSON data
            headers (Dict[str, str], optional): Request headers
            timeout (Optional[int], optional): Request timeout
            retry_count (int): Number of retry attempts made

        Returns:
            requests.Response: The response from the API
        """
        # Merge auth headers with provided headers
        all_headers = self.get_auth_headers()
        if headers:
            all_headers.update(headers)

        url = self.get_full_url(endpoint)
        response = requests.put(url, data=data, json=json,
                                headers=all_headers, timeout=timeout)

        # Define retry function
        def retry(new_retry_count):
            return self.put(endpoint, data, json, headers, timeout, new_retry_count)

        # Handle response and potential token refresh
        response, was_retried = self._handle_response(
            response, retry, retry_count)

        return response

    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None,
               timeout: Optional[int] = None, retry_count: int = 0) -> requests.Response:
        """Make a DELETE request to the API with automatic token refresh

        Args:
            endpoint (str): The API endpoint
            headers (Dict[str, str], optional): Request headers
            timeout (Optional[int], optional): Request timeout
            retry_count (int): Number of retry attempts made

        Returns:
            requests.Response: The response from the API
        """
        # Merge auth headers with provided headers
        all_headers = self.get_auth_headers()
        if headers:
            all_headers.update(headers)

        url = self.get_full_url(endpoint)
        response = requests.delete(url, headers=all_headers, timeout=timeout)

        # Define retry function
        def retry(new_retry_count):
            return self.delete(endpoint, headers, timeout, new_retry_count)

        # Handle response and potential token refresh
        response, was_retried = self._handle_response(
            response, retry, retry_count)

        return response
