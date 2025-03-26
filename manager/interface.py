import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, QPushButton,
                             QDesktopWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QStackedWidget)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.label_username = QLabel("Username", self)
        self.label_password = QLabel("Password", self)
        self.username_field = QLineEdit(self)
        self.password_field = QLineEdit(self)
        self.button_login = QPushButton("Login", self)
        self.button_signup = QPushButton("Sign Up", self)
        self.initUI()

    def initUI(self):
        # Create the stacked widget to manage screens
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        # Create the login page
        self.login_page = QWidget()
        self.create_login_page()

        # Create the home page (another screen to switch to after login/signup)
        self.home_page = QWidget()
        self.create_home_page()

        # Add pages to the stacked widget
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.home_page)

        # Set initial screen to login page
        self.stacked_widget.setCurrentWidget(self.login_page)

        # Main window settings
        self.setWindowTitle("Login Screen")
        self.setGeometry(0, 0, 1024, 768)
        self.center()

    def create_login_page(self):
        # Set up fonts and styles
        font = QFont("Arial", 16)
        self.label_username.setFont(font)
        self.label_password.setFont(font)
        self.username_field.setFont(font)
        self.password_field.setFont(font)
        self.button_login.setFont(font)
        self.button_signup.setFont(font)

        # Customize label styles
        self.label_username.setStyleSheet("color: black; font-weight: bold;")
        self.label_password.setStyleSheet("color: black; font-weight: bold;")

        # Set input field types (password for password field)
        self.password_field.setEchoMode(QLineEdit.Password)

        # Set up button style
        self.button_login.setStyleSheet("font-size: 18px; padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;")
        self.button_signup.setStyleSheet("font-size: 18px; padding: 10px; background-color: #2196F3; color: white; border-radius: 5px;")

        # Set up button click actions
        self.button_login.clicked.connect(self.on_click_login)
        self.button_signup.clicked.connect(self.on_click_signup)

        # Set up text field height
        self.username_field.setFixedHeight(40)  # Increase height for better visibility
        self.password_field.setFixedHeight(40)  # Increase height for better visibility

        # Create a layout
        layout = QVBoxLayout()  # Use a vertical layout for stacking widgets
        layout.setSpacing(20)  # Reduce vertical spacing between fields and buttons
        layout.setContentsMargins(100, 50, 100, 50)  # Add margins to the sides

        # Add the title at the top
        title = QLabel("Resume Builder", self)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setStyleSheet("color: #4CAF50; padding-bottom: 20px;")  # Set color and margin for space below title
        layout.addWidget(title)

        # Add widgets to the layout
        layout.addWidget(self.label_username)
        layout.addWidget(self.username_field)
        layout.addWidget(self.label_password)
        layout.addWidget(self.password_field)
        layout.addWidget(self.button_login)
        layout.addWidget(self.button_signup)

        # Add stretch at the bottom to keep everything centered vertically
        layout.addStretch(1)

        self.login_page.setLayout(layout)

    def create_home_page(self):
        # Create a simple home screen layout
        label_welcome = QLabel("Welcome to the Home Screen!", self)
        label_welcome.setFont(QFont("Arial", 24))
        label_welcome.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(label_welcome)

        self.home_page.setLayout(layout)

    def on_click_login(self):
        # Logic for logging in (just an example)
        print("Logged in successfully!")
        # Switch to home page after login
        self.stacked_widget.setCurrentWidget(self.home_page)

    def on_click_signup(self):
        # Logic for signing up (just an example)
        print("Signed up successfully!")
        # Switch to home page after signup
        self.stacked_widget.setCurrentWidget(self.home_page)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
