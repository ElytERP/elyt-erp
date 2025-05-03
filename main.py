from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
import sys
import yaml
from cryptography.fernet import Fernet
import os
import psycopg2  # PostgreSQL library

# Ensure the configs directory exists
configs_dir = "configs"
os.makedirs(configs_dir, exist_ok=True)  # Add exist_ok=True to avoid FileExistsError

# Paths for the key and YAML files
key_file_path = os.path.join(configs_dir, "key.key")
yaml_file_path = os.path.join(configs_dir, "credentials.yaml")

# Check if the key file exists
if os.path.exists(key_file_path):
    # Load the existing encryption key
    with open(key_file_path, "rb") as key_file:
        key = key_file.read()
else:
    # Generate a new encryption key and save it
    key = Fernet.generate_key()
    with open(key_file_path, "wb") as key_file:
        key_file.write(key)

cipher = Fernet(key)

class ServerCredentialsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Server Credentials")
        self.setFixedSize(300, 300)

        # Layout for the dialog
        layout = QVBoxLayout()

        # Add input fields
        layout.addWidget(QLabel("postgreSQL Server Address:"))
        self.server_address_input = QLineEdit()
        layout.addWidget(self.server_address_input)

        layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit()
        self.port_input.setText("5432")  # Set default value for the port
        layout.addWidget(self.port_input)

        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Add Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_credentials)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_credentials(self):
        # Get user input
        server_address = self.server_address_input.text()
        port = self.port_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        database_name = "postgres"  

        # Attempt to connect to PostgreSQL
        try:
            connection = psycopg2.connect(
                host=server_address,
                port=port,
                user=username,
                password=password,
                dbname=database_name  # Specify the database name explicitly
            )
            connection.close()  # Close the connection if successful

            # Encrypt the password
            encrypted_password = cipher.encrypt(password.encode())

            # Save credentials to a YAML file
            credentials = {
                "server_address": server_address,
                "port": port,
                "username": username,
                "password": encrypted_password.decode()  # Save encrypted password as a string
            }

            with open(yaml_file_path, "w") as file:
                yaml.dump(credentials, file)

            # Show a success dialog
            QMessageBox.information(self, "Success", f"Connection successful! Credentials saved to {yaml_file_path}.")
            self.accept()

        except psycopg2.Error as e:
            # Show an error dialog if the connection fails
            QMessageBox.critical(self, "Connection Failed", f"Failed to connect to PostgreSQL server:\n{e}")

def main_window():
    # Create the application
    app = QApplication(sys.argv)
    
    # Create the main window
    main_window = QMainWindow()
    main_window.setWindowTitle("ERP System")
    
    # Set the window to auto-maximize
    main_window.showMaximized()
    
    # Create a menu bar
    menu_bar = QMenuBar(main_window)
    main_window.setMenuBar(menu_bar)
    
    # Add menus to the menu bar
    file_menu = menu_bar.addMenu("Company")
    help_menu = menu_bar.addMenu("Help")
    
    # Add actions to the File menu
    new_action = QAction("Open Company", main_window)
    open_action = QAction("Create Company", main_window)
    server_credentials_action = QAction("Server Credentials", main_window)
    exit_action = QAction("Exit", main_window)
    exit_action.triggered.connect(app.quit)
    
    file_menu.addAction(new_action)
    file_menu.addAction(open_action)
    file_menu.addSeparator()
    file_menu.addAction(server_credentials_action)
    file_menu.addSeparator()
    file_menu.addAction(exit_action)

    # Connect "Server Credentials" action to open the dialog
    server_credentials_action.triggered.connect(lambda: ServerCredentialsDialog(main_window).exec())

    # Execute the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main_window()