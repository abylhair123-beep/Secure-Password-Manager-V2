from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QInputDialog, QMessageBox, QApplication, QAbstractItemView, QLineEdit, QFileDialog, QHeaderView )
from PySide6.QtGui import QIcon
from core.storage import load_passwords, save_passwords
from core.crypto import encrypt_password, decrypt_password, generate_key
from utils.password_generator import generate_password
import csv
import os


class MainWindow(QWidget):
    def __init__(self, master_password: str):
        super().__init__()
        self.setWindowTitle("Менеджер паролей")
        self.setFixedSize(850, 500)

        self.master_password = master_password
        self.key = generate_key(master_password)

#Темная тема
        self.setStyleSheet("""
            QWidget { font-family: Arial; font-size: 12pt; background-color: #2b2b2b; color: #eee; }
            QLineEdit { padding: 4px; font-size: 11pt; background-color: #3c3c3c; color: #eee; border-radius: 4px; }
            QTableWidget { gridline-color: #555; background-color: #3c3c3c; color: #eee; }
            QPushButton { background-color: #4CAF50; color: white; padding: 5px; border-radius: 4px; }
            QPushButton:hover { background-color: #45a049; }
        """)

#Поиск пароля
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по сервису или логину...")
        self.search_input.textChanged.connect(self.filter_table)

#Таблица паролей
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Сервис", "Логин", "Пароль"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

#Создин черный цвет
        self.table.horizontalHeader().setStyleSheet(
            "QHeaderView::section { background-color: white; color: black; font-weight: bold; }"
        )
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setStyleSheet(
            "QHeaderView::section { background-color: white; color: black; font-weight: bold; }"
        )

        self.load_table()

#Кнопки
        self.add_btn = QPushButton("Добавить")
        self.add_btn.setToolTip("Добавить новый пароль")
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.setToolTip("Удалить выбранный пароль")
        self.show_btn = QPushButton("Показать/Скрыть")
        self.show_btn.setToolTip("Показать или скрыть пароль")
        self.copy_btn = QPushButton("Копировать")
        self.copy_btn.setToolTip("Скопировать пароль в буфер обмена")
        self.generate_btn = QPushButton("Сгенерировать")
        self.generate_btn.setToolTip("Сгенерировать безопасный пароль")
        self.export_btn = QPushButton("Экспорт")
        self.export_btn.setToolTip("Экспорт паролей в CSV")
        self.import_btn = QPushButton("Импорт")
        self.import_btn.setToolTip("Импорт паролей из CSV")

#connect кнопок
        self.add_btn.clicked.connect(self.add_password)
        self.delete_btn.clicked.connect(self.delete_password)
        self.show_btn.clicked.connect(self.show_hide_password)
        self.copy_btn.clicked.connect(self.copy_password)
        self.generate_btn.clicked.connect(self.generate_password_dialog)
        self.export_btn.clicked.connect(self.export_passwords)
        self.import_btn.clicked.connect(self.import_passwords)

#Дизайн для кнопок
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.show_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.import_btn)

#Дизайн
        layout = QVBoxLayout()
        layout.addWidget(self.search_input)
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

#Методы
    def load_table(self):
        self.table.setRowCount(0)
        self.passwords = load_passwords()
        for row_idx, entry in enumerate(self.passwords):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(entry["service"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(entry["login"]))
            try:
                decrypted = decrypt_password(entry["password"].encode(), self.key)
            except:
                decrypted = "Ошибка"
            self.table.setItem(row_idx, 2, QTableWidgetItem("*" * len(decrypted)))

    def add_password(self):
        service, ok1 = QInputDialog.getText(self, "Сервис", "Введите название сервиса:")
        if not ok1 or not service: return
        login, ok2 = QInputDialog.getText(self, "Логин", "Введите логин:")
        if not ok2 or not login: return
        password, ok3 = QInputDialog.getText(self, "Пароль", "Введите пароль:")
        if not ok3 or not password: return

        encrypted = encrypt_password(password, self.key)
        self.passwords.append({"service": service, "login": login, "password": encrypted.decode()})
        save_passwords(self.passwords)
        self.load_table()
        QMessageBox.information(self, "Успех", "Пароль добавлен!")

    def delete_password(self):
        selected = self.table.currentRow()
        if selected == -1: return
        confirm = QMessageBox.question(self, "Подтвердите удаление", "Удалить выбранный пароль?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.passwords.pop(selected)
            save_passwords(self.passwords)
            self.load_table()

    def show_hide_password(self):
        selected = self.table.currentRow()
        if selected == -1: return
        current_text = self.table.item(selected, 2).text()
        decrypted = decrypt_password(self.passwords[selected]["password"].encode(), self.key)
        if current_text.startswith("*"):
            self.table.setItem(selected, 2, QTableWidgetItem(decrypted))
        else:
            self.table.setItem(selected, 2, QTableWidgetItem("*" * len(decrypted)))

    def copy_password(self):
        selected = self.table.currentRow()
        if selected == -1: return
        decrypted = decrypt_password(self.passwords[selected]["password"].encode(), self.key)
        QApplication.clipboard().setText(decrypted)
        QMessageBox.information(self, "Скопировано", "Пароль скопирован в буфер обмена")

    def filter_table(self):
        text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            service_item = self.table.item(row, 0).text().lower()
            login_item = self.table.item(row, 1).text().lower()
            self.table.setRowHidden(row, not (text in service_item or text in login_item))

    def generate_password_dialog(self):
        length, ok = QInputDialog.getInt(self, "Генерация пароля", "Введите длину пароля:", 12, 4, 64)
        if not ok: return
        password = generate_password(length)
        QMessageBox.information(self, "Сгенерированный пароль", f"Пароль:\n{password}")

        add_now = QMessageBox.question(self, "Добавить пароль", "Хотите добавить этот пароль сейчас?",
                                       QMessageBox.Yes | QMessageBox.No)
        if add_now == QMessageBox.Yes:
            service, ok1 = QInputDialog.getText(self, "Сервис", "Введите название сервиса:")
            if not ok1 or not service: return
            login, ok2 = QInputDialog.getText(self, "Логин", "Введите логин:")
            if not ok2 or not login: return
            encrypted = encrypt_password(password, self.key)
            self.passwords.append({"service": service, "login": login, "password": encrypted.decode()})
            save_passwords(self.passwords)
            self.load_table()
            QMessageBox.information(self, "Успех", "Пароль добавлен!")

    def export_passwords(self):
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт паролей", "", "CSV файлы (*.csv)")
        if not path: return
        try:
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Сервис", "Логин", "Пароль"])
                for entry in self.passwords:
                    decrypted = decrypt_password(entry["password"].encode(), self.key)
                    writer.writerow([entry["service"], entry["login"], decrypted])
            QMessageBox.information(self, "Успех", f"Пароли экспортированы в {path}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось экспортировать: {e}")

    def import_passwords(self):
        path, _ = QFileDialog.getOpenFileName(self, "Импорт паролей", "", "CSV файлы (*.csv)")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    service = row["Сервис"]
                    login = row["Логин"]
                    password = row["Пароль"]
                    encrypted = encrypt_password(password, self.key)
                    self.passwords.append({"service": service, "login": login, "password": encrypted.decode()})
            save_passwords(self.passwords)
            self.load_table()
            QMessageBox.information(self, "Успех", f"Пароли импортированы из {path}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось импортировать: {e}")