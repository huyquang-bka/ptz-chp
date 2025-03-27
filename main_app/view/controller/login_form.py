from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QIcon
from main_app.view.ui.login_form import Ui_Dialog
from main_app.model.language_manager import LanguageManager
from main_app.utils.ui_helpers import setup_language_icons, setup_logo_image, set_button_state


class LoginForm(QDialog):
    def __init__(self, parent=None):
        super(LoginForm, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # set window logo
        self.setWindowIcon(QIcon("resources/images/logo.png"))

        # Get language manager instance
        self.language_manager = LanguageManager()

        # Connect language manager signal to update UI
        self.language_manager.language_changed.connect(self.update_ui_texts)

        # Set up logo
        setup_logo_image(self.ui.qlabel_logo)

        # Set up language icons
        setup_language_icons(self.ui)

        # Connect language change signal
        self.ui.comboBox_language.currentIndexChanged.connect(
            self.on_language_changed)

        # Initialize UI with current language
        self.update_ui_texts()

    def on_language_changed(self, index):
        # Handle language change
        language_code = "en" if index == 0 else "vi"
        self.language_manager.set_language(language_code)

    def update_ui_texts(self):
        """Update all UI texts based on current language"""
        lm = self.language_manager

        # Update window title
        self.setWindowTitle(lm.get_text("login_window_title"))

        # Update combo box items
        self.ui.comboBox_language.setItemText(
            0, lm.get_text("language_english"))
        self.ui.comboBox_language.setItemText(
            1, lm.get_text("language_vietnamese"))

        # Update labels
        self.ui.qlabel_title.setText(lm.get_text("welcome_back"))
        self.ui.qlabel_username.setText(lm.get_text("username"))
        self.ui.qlabel_password.setText(lm.get_text("password"))

        # Update placeholders
        self.ui.qline_username.setPlaceholderText(
            lm.get_text("username_placeholder"))
        self.ui.qline_password.setPlaceholderText(
            lm.get_text("password_placeholder"))

        # Update checkbox and button
        self.ui.qcheckbox_remember_me.setText(lm.get_text("remember_me"))
        self.ui.btn_login.setText(lm.get_text("login_button"))

    def set_login_button_state(self, enabled, text=None):
        """Set the state of the login button"""
        set_button_state(self.ui.btn_login, enabled, text)

    def reset_login_button(self):
        """Reset login button to its original state"""
        self.set_login_button_state(
            True, self.language_manager.get_text("login_button"))

    def show_login_form(self):
        """Show the login form"""
        self.show()

    def set_credentials(self, username, password, remember_me):
        """Set the credentials in the UI"""
        self.ui.qline_username.setText(username)
        self.ui.qline_password.setText(password)
        self.ui.qcheckbox_remember_me.setChecked(remember_me)
