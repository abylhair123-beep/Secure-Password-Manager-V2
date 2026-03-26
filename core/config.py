import os

DATA_DIR = "data"
MASTER_PASSWORD_FILE = os.path.join(DATA_DIR, "master.hash")
os.makedirs(DATA_DIR, exist_ok=True)