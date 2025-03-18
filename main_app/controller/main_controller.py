from PyQt5.QtWidgets import QMainWindow, QMessageBox
from main_app.view.controller.login_form import LoginForm
from main_app.view.controller.main_window import MainWindow
from main_app.model.language_manager import LanguageManager
from main_app.service.auth_service import AuthService
from main_app.utils.ui_helpers import show_message_box


class MainController(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize language manager
        self.language_manager = LanguageManager()

        # Initialize authentication service
        self.auth_service = AuthService()

        # Initialize login form and main window
        self.login_form = LoginForm()
        self.main_window = None  # Will be initialized after successful login

        # Initialize user data
        self.user_data = {}

        # Connect login form signals
        self.login_form.ui.btn_login.clicked.connect(self.on_login)

        # Load saved credentials
        self.load_saved_credentials()

        # Show login form
        self.login_form.show_login_form()

    def load_saved_credentials(self):
        """Load saved credentials into the login form"""
        username, password, remember_me = self.auth_service.load_saved_credentials()
        self.login_form.set_credentials(username, password, remember_me)

    def on_login(self):
        """Handle login button click and authentication"""
        username = self.login_form.ui.qline_username.text().strip()
        password = self.login_form.ui.qline_password.text().strip()
        remember_me = self.login_form.ui.qcheckbox_remember_me.isChecked()

        if not username or not password:
            print("Login failed: Username and password required when login")
            show_message_box(
                self.language_manager.get_text("login_error_title"),
                self.language_manager.get_text("login_error_empty_fields"),
                parent=self.login_form
            )
            return

        # Disable login button and change its appearance
        self.login_form.set_login_button_state(
            False, self.language_manager.get_text("logging_in"))

        # Authenticate user
        success, result = self.auth_service.authenticate(username, password)

        if success:
            # Save credentials if remember me is checked
            self.auth_service.save_credentials(username, password, remember_me)

            # Save user data
            self.user_data = self.auth_service.save_user_data(result)

            print(f"Login successful for user: {username}")

            # Initialize and show main window immediately
            self.main_window = MainWindow(self.user_data)
            self.login_form.hide()
            self.show_main_window()
        else:
            # Handle failed login
            error_message = result
            print(f"Login failed: {error_message}")

            QMessageBox.critical(
                self.login_form,
                self.language_manager.get_text("login_failed_title"),
                error_message
            )

            # Re-enable login button
            self.login_form.reset_login_button()

    def show_main_window(self):
        """Show the main window"""
        if self.main_window:
            self.main_window.show_main_window()
