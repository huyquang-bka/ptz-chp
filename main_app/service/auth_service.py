from PyQt5.QtCore import QSettings
from main_app.model.api_route import ApiRoute
from main_app.network.custom_http import CustomHTTPRequest
from main_app.model.auth import Auth


class AuthService:
    def __init__(self):
        # Initialize API routes
        self.api_route = ApiRoute()

        # Initialize HTTP client
        self.http_client = CustomHTTPRequest(
            self.api_route.base_url,
            self.api_route.additional_route
        )

    def authenticate(self, username, password):
        """Authenticate user with API

        Returns:
            tuple: (success, response_data or error_message)
        """
        try:
            # Prepare login payload from API route configuration
            login_payload = self.api_route.login_payload.copy()
            login_payload["username"] = username
            login_payload["password"] = password

            # Make the login request
            response = self.http_client.post(
                self.api_route.login_route,
                json=login_payload
            )
            # Check response status
            if response.status_code == 200:
                # Parse response data
                response_data = response.json()
                return True, response_data
            else:
                # Handle failed login
                error_message = "Login failed"

                # Try to get more specific error message from response
                try:
                    error_data = response.json()
                    if "error_description" in error_data:
                        error_message = error_data["error_description"]
                    elif "message" in error_data:
                        error_message = error_data["message"]
                except:
                    # If we can't parse the error, use the default message
                    pass

                return False, error_message

        except Exception as e:
            return False, str(e)

    def save_credentials(self, username, password, remember_me):
        """Save credentials if remember me is checked"""
        settings = QSettings("PTZ-CHP", "LoginSettings")

        if remember_me:
            settings.setValue("remember_me", True)
            settings.setValue("username", username)
            settings.setValue("password", password)
        else:
            settings.setValue("remember_me", False)
            settings.remove("username")
            settings.remove("password")

        settings.sync()

    def load_saved_credentials(self):
        """Load saved username and password if remember me was checked

        Returns:
            tuple: (username, password, remember_me)
        """
        settings = QSettings("PTZ-CHP", "LoginSettings")
        remember_me = settings.value("remember_me", False, type=bool)

        if remember_me:
            username = settings.value("username", "")
            password = settings.value("password", "")
            return username, password, True

        return "", "", False

    def save_user_data(self, response_data):
        """Save important user data for later use

        Returns:
            dict: User data dictionary
        """
        # Store in application settings
        settings = QSettings("PTZ-CHP", "UserData")
        settings.setValue(
            "access_token", response_data.get("access_token", ""))
        settings.setValue(
            "refresh_token", response_data.get("refresh_token", ""))
        settings.setValue("fullName", response_data.get("fullName", ""))
        settings.setValue("username", response_data.get("username", ""))
        settings.setValue("userId", response_data.get("userId", 0))
        settings.setValue("comId", response_data.get("comId", 0))
        settings.sync()

        # Return user data dictionary
        auth = Auth()
        auth.from_json(response_data)

        return auth

    def refresh_token(self):
        """Refresh the access token"""
        return self.http_client.refresh_token()
