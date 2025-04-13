import os
import sys
import subprocess
import shutil
import urllib.request
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QTextEdit, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt

LICENSE_FILE_PATH = "LICENSE"  # Adjust this if needed


class WelcomeScreen(QWidget):
    def __init__(self, next_callback):
        super().__init__()
        self.next_callback = next_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Welcome to Elyt ERP Setup")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        message = QLabel("This wizard will guide you through the installation of Elyt ERP.\nClick 'Next' to begin.")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)

        next_button = QPushButton("Next")
        next_button.setFixedWidth(120)
        next_button.clicked.connect(self.next_callback)

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(message)
        layout.addStretch()
        layout.addWidget(next_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)


class LicenseScreen(QWidget):
    def __init__(self, next_callback):
        super().__init__()
        self.next_callback = next_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Elyt ERP License Agreement")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.license_box = QTextEdit()
        self.license_box.setReadOnly(True)

        try:
            with open(LICENSE_FILE_PATH, "r", encoding="utf-8") as f:
                self.license_box.setText(f.read())
        except Exception as e:
            self.license_box.setText("Failed to load license file:\n" + str(e))

        self.agree_checkbox = QCheckBox("I accept the terms of the license agreement.")

        next_button = QPushButton("Next")
        next_button.clicked.connect(self.on_next)

        layout.addWidget(title)
        layout.addWidget(self.license_box)
        layout.addWidget(self.agree_checkbox)
        layout.addWidget(next_button, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def on_next(self):
        if not self.agree_checkbox.isChecked():
            QMessageBox.warning(self, "Agreement Required", "You must accept the license to continue.")
        else:
            self.next_callback()
            
class PostgresInstallScreen(QWidget):
    def __init__(self, next_callback):
        super().__init__()
        self.next_callback = next_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.title = QLabel("Elyt ERP - PostgreSQL Setup")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title)

        self.status_label = QLabel("Checking if PostgreSQL is installed...")
        layout.addWidget(self.status_label)

        self.install_button = QPushButton("Download and Install PostgreSQL")
        self.install_button.clicked.connect(self.download_and_install_postgres)
        self.install_button.setVisible(False)
        layout.addWidget(self.install_button)

        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.continue_next)
        self.continue_button.setVisible(False)
        layout.addWidget(self.continue_button)

        self.setLayout(layout)
        self.check_postgres()

    def find_psql(self):
        # First check PATH
        psql_path = shutil.which("psql")
        if psql_path:
            return psql_path
    
        # Check common install directories (Windows)
        possible_dirs = [
            r"C:\Program Files\PostgreSQL",
            r"C:\Program Files (x86)\PostgreSQL"
        ]
    
        for base in possible_dirs:
            if os.path.exists(base):
                for sub in os.listdir(base):
                    psql_candidate = os.path.join(base, sub, "bin", "psql.exe")
                    if os.path.isfile(psql_candidate):
                        return psql_candidate
    
        return None
    
    def check_postgres(self):
        psql_path = self.find_psql()

        if psql_path:
            self.status_label.setText(f"PostgreSQL found at: {psql_path}")
            self.continue_button.setVisible(True)
        else:
            self.status_label.setText("PostgreSQL not found.")
            self.install_button.setVisible(True)
    
    def download_and_install_postgres(self):
        self.status_label.setText("Downloading installer...")

        installer_url = "https://get.enterprisedb.com/postgresql/postgresql-16.2-1-windows-x64.exe"
        installer_path = os.path.join(os.getcwd(), "postgres_installer.exe")

        try:
            urllib.request.urlretrieve(installer_url, installer_path)
            self.status_label.setText("Installer downloaded. Launching...")
            subprocess.Popen([installer_path], shell=True)

            QMessageBox.information(
                self, "Installation",
                "The PostgreSQL installer has been launched.\n"
                "Please complete the installation and return here to continue."
            )

        except Exception as e:
            QMessageBox.critical(self, "Download Error", f"Failed to download installer:\n{str(e)}")
            return

    def continue_next(self):
        self.status_label.setText("Verifying PostgreSQL installation...")
        if shutil.which("psql"):
            self.status_label.setText("PostgreSQL successfully installed.")
            self.open_postgres_port()
            self.next_callback()
        else:
            QMessageBox.warning(self, "PostgreSQL Missing", "PostgreSQL is still not installed.")

    def open_postgres_port(self):
        try:
            subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                 'name=PostgreSQL', 'dir=in', 'action=allow', 'protocol=TCP', 'localport=5432'],
                check=True
            )
            self.status_label.setText("PostgreSQL port 5432 opened on LAN.")
        except Exception as e:
            QMessageBox.warning(self, "Firewall Error", f"Failed to open port:\n{e}")


class FinishScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Elyt ERP Installation Complete")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        message = QLabel("Thank you for installing Elyt ERP.\nYou may now close this window or launch the application.")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)

        close_button = QPushButton("Finish")
        close_button.setFixedWidth(120)
        close_button.clicked.connect(lambda: QApplication.quit())

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(message)
        layout.addStretch()
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)


class InstallerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elyt ERP Installer")
        self.setGeometry(100, 100, 600, 400)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome_screen = WelcomeScreen(self.show_license_screen)
        self.license_screen = LicenseScreen(self.show_postgres_screen)
        self.postgres_screen = PostgresInstallScreen(self.show_finish_screen)
        self.finish_screen = FinishScreen()

        self.stack.addWidget(self.welcome_screen)
        self.stack.addWidget(self.license_screen)
        self.stack.addWidget(self.postgres_screen)
        self.stack.addWidget(self.finish_screen)

        self.stack.setCurrentWidget(self.welcome_screen)

    def show_license_screen(self):
        self.stack.setCurrentWidget(self.license_screen)

    def show_postgres_screen(self):
        self.stack.setCurrentWidget(self.postgres_screen)

    def show_finish_screen(self):
        self.stack.setCurrentWidget(self.finish_screen)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InstallerApp()
    window.show()
    sys.exit(app.exec())
