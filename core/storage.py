import json
import os
from core.config import DATA_DIR

PASSWORD_FILE = os.path.join(DATA_DIR, "password.json")

def load_passwords() -> list:
    if not os.path.exists(PASSWORD_FILE):
        return []

    with open(PASSWORD_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_passwords(passwords: list):
    with open(PASSWORD_FILE, "w", encoding="utf-8") as f:
        json.dump(passwords, f, indent=4)