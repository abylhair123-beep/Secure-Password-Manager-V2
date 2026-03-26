from cryptography.fernet import Fernet
import base64
import hashlib

def generate_key(master_password: str) -> bytes:
    digest = hashlib.sha256(master_password.encode()).digest()
    return base64.b64encode(digest)


def encrypt_password(password: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(password.encode())

def decrypt_password(cipher_text: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(cipher_text).decode()
