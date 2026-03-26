import random
import string

def generate_password(length: int = 12) -> str:
    if length < 4:
        length = 4
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))