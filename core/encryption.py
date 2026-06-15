import base64, os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
KEY_FILE = DATA_DIR / "secret.key"

def _load_key():
    key = KEY_FILE.read_bytes()
    if len(key) not in (16,24,32):
        from hashlib import sha256
        key = sha256(key).digest()
    return key

def encrypt_bytes(data: bytes):
    key = _load_key()
    cipher = AES.new(key, AES.MODE_CBC)
    ct = cipher.encrypt(pad(data, AES.block_size))
    return base64.b64encode(cipher.iv).decode(), base64.b64encode(ct).decode()

def decrypt_to_bytes(iv_b64: str, ct_b64: str):
    key = _load_key()
    iv = base64.b64decode(iv_b64)
    ct = base64.b64decode(ct_b64)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt
