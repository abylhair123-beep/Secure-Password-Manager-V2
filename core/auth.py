import os
import bcrypt
from core.config import MASTER_PASSWORD_FILE


def master_password_exists() -> bool:
    return os.path.exists(MASTER_PASSWORD_FILE)


def create_master_password(password: str) -> None:
    if master_password_exists():
        raise Exception("Пароль уже существует")

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    with open(MASTER_PASSWORD_FILE, "wb") as f:
        f.write(hashed)


def verify_master_password(password: str) -> bool:

    if not master_password_exists():
        raise Exception("Пароль не установлен")

    with open(MASTER_PASSWORD_FILE, "rb") as f:
        stored_hash = f.read()
    return bcrypt.checkpw(password.encode(), stored_hash)