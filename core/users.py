import json, hashlib
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"

def _load_users():
    return json.loads(USERS_FILE.read_text())

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def authenticate(username: str, password: str):
    users = _load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return {"username": username, "role": users[username]["role"]}
    return None
