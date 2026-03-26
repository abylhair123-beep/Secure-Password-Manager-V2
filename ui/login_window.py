from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from core.auth import master_password_exists, create_master_password, verify_master_password
from ui.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Password Manager")
        self.setFixedSize(300, 150)

        self.label = QLabel("Enter Master Password:")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.button = QPushButton()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_password)
        layout.addWidget(self.button)
        self.setLayout(layout)

        if master_password_exists():
            self.button.setText("Unlock")
        else:
            self.button.setText("Create")

        self.button.clicked.connect(self.handle_password)

    def handle_password(self):
        password = self.input_password.text().strip()
        if not password:
            QMessageBox.warning(self, "Error", "Password cannot be empty!")
            return

        if self.button.text() == "Create":
            try:
                create_master_password(password)
                QMessageBox.information(self, "Success", "Master password created!")
                self.open_main_window()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
        else:
            if verify_master_password(password):
                self.open_main_window()
            else:
                QMessageBox.warning(self, "Error", "Wrong password!")

    def open_main_window(self):
        self.main_window = MainWindow(self.input_password.text())
        self.main_window.show()
        self.close()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())