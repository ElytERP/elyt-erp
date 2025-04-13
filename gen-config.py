import sys
import os
import yaml
import psycopg2
from psycopg2 import OperationalError
from cryptography.fernet import Fernet
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QMessageBox, QMenuBar, QTextEdit
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

class PostgresConnectionChecker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PostgreSQL Connection Checker")
        self.setGeometry(100, 100, 400, 500)

        # Central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Input fields
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Host (e.g., localhost)")
        main_layout.addWidget(self.host_input)

        self.dbname_input = QLineEdit()
        self.dbname_input.setPlaceholderText("Database Name")
        main_layout.addWidget(self.dbname_input)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        main_layout.addWidget(self.user_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        main_layout.addWidget(self.password_input)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port (default: 5432)")
        self.port_input.setText("5432")  # Set default port value
        main_layout.addWidget(self.port_input)

        # Check connection button
        self.check_button = QPushButton("Check Connection")
        self.check_button.clicked.connect(self.check_connection)
        main_layout.addWidget(self.check_button)

        # Logs box
        self.logs_box = QTextEdit()
        self.logs_box.setReadOnly(True)  # Make it read-only
        self.logs_box.setPlaceholderText("Connection logs will appear here...")
        main_layout.addWidget(self.logs_box)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Menu bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Add "View" menu
        view_menu = self.menu_bar.addMenu("View")

        # Add "Enable Dark Mode" action
        self.dark_mode_action = QAction("Enable Dark Mode", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)

        # Default theme
        self.is_dark_mode = False
        self.set_light_mode()  # Set light mode as the default theme

        # Encryption key
        self.encryption_key = self.generate_and_save_key()
        self.cipher = Fernet(self.encryption_key)

    def generate_and_save_key(self):
        # Ensure the configs directory exists
        os.makedirs("configs", exist_ok=True)

        key_file_path = "configs/encryption.key"

        # Check if the key file already exists
        if os.path.exists(key_file_path):
            with open(key_file_path, "rb") as key_file:
                key = key_file.read()
            self.logs_box.append("Using existing encryption key from configs/encryption.key.")
        else:
            # Generate a new Fernet key
            key = Fernet.generate_key()

            # Save the key to a file
            with open(key_file_path, "wb") as key_file:
                key_file.write(key)

            self.logs_box.append("Encryption key saved to configs/encryption.key.")

        return key

    def check_connection(self):
        host = self.host_input.text()
        dbname = self.dbname_input.text()
        user = self.user_input.text()
        password = self.password_input.text()
        port = self.port_input.text() or "5432"

        try:
            # Attempt to connect to the PostgreSQL server
            connection = psycopg2.connect(
                host=host,
                dbname=dbname,
                user=user,
                password=password,
                port=int(port)
            )
            self.logs_box.append("Connection successful!")
            QMessageBox.information(self, "Success", "Connection to PostgreSQL server successful!")
            connection.close()

            # Save connection details to encrypted YAML file
            self.save_connection_details(host, dbname, user, password, port)

        except OperationalError as e:
            error_message = f"Failed to connect to PostgreSQL server: {e}"
            self.logs_box.append(error_message)
            QMessageBox.critical(self, "Error", error_message)

    def save_connection_details(self, host, dbname, user, password, port):
        # Connection details
        connection_details = {
    "database": {
        "type": "postgresql",
        "host": host,
        "name": dbname,
        "user": user,
        "password": password,
        "port": int(port),
    }
}


        # Encrypt the connection details
        encrypted_data = self.cipher.encrypt(yaml.dump(connection_details).encode())

        # Ensure the configs directory exists
        os.makedirs("configs", exist_ok=True)

        # Save the encrypted data to a YAML file
        with open("configs/connection.yml", "wb") as file:
            file.write(encrypted_data)

        self.logs_box.append("Connection details saved to configs/connection.yml (encrypted).")

    def toggle_dark_mode(self, checked):
        if checked:
            self.set_dark_mode()
            self.dark_mode_action.setText("Disable Dark Mode")
        else:
            self.set_light_mode()
            self.dark_mode_action.setText("Enable Dark Mode")

    def set_dark_mode(self):
        dark_stylesheet = """
            QMainWindow {
                background-color: #121212;
                color: #ffffff;
            }
            QLabel, QLineEdit, QPushButton, QTextEdit {
                color: #ffffff;
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """
        self.setStyleSheet(dark_stylesheet)
        self.is_dark_mode = True

    def set_light_mode(self):
        light_stylesheet = """
            QMainWindow {
                background-color: #f5f5f5;
                color: #000000;
            }
            QLabel, QLineEdit, QPushButton, QTextEdit {
                color: #000000;
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #d6d6d6;
            }
        """
        self.setStyleSheet(light_stylesheet)
        self.is_dark_mode = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PostgresConnectionChecker()
    window.show()
    sys.exit(app.exec())