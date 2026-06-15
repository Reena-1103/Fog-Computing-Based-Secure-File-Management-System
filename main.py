# main.py
# Fog Computing Encrypted Control System - main runner
# Save this file as main.py in your project root and run `python main.py`.

import os
import json
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Import FileUI class provided earlier
from ui.file_ui import FileUI

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

SECRET_KEY_PATH = os.path.join("data", "secret.key")


def ensure_data_dirs():
    os.makedirs("data", exist_ok=True)
    os.makedirs(os.path.join("data", "files"), exist_ok=True)


class FogApp:
    def __init__(self, root):
        ensure_data_dirs()
        self.root = root
        self.root.title("Fog Computing Encrypted Control System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")

        # Application state
        self.current_user = None
        self.files = {}       # optional in-memory cache
        self.audit_log = []

        # users - hashed passwords (sha256)
        self.users = {
            "admin": {"password": self.hash_password("admin123"), "role": "administrator"},
            "company": {"password": self.hash_password("company123"), "role": "company"},
            "cloud": {"password": self.hash_password("cloud123"), "role": "cloud"},
            "auditor": {"password": self.hash_password("auditor123"), "role": "auditor"},
        }

        # encryption key (16/24/32 bytes) - stored in data/secret.key (auto-generate once)
        self._key = None
        self.load_or_create_key()

        # main frames
        self.top_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.top_frame.pack(fill=tk.X)
        self.content_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # attach FileUI helper
        self.file_ui = FileUI(self)

        # show login UI initially
        self.setup_login_ui()

    # ----------------- encryption helpers -----------------
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def load_or_create_key(self):
        """Load a 32-byte key from file or create a new random one and save."""
        if os.path.exists(SECRET_KEY_PATH):
            with open(SECRET_KEY_PATH, "rb") as f:
                self._key = f.read()
        else:
            rnd = os.urandom(32)
            # store raw bytes
            with open(SECRET_KEY_PATH, "wb") as f:
                f.write(rnd)
            self._key = rnd

    def encrypt_data(self, data_bytes: bytes):
        """Return (iv_b64, ciphertext_b64)"""
        if not self._key:
            raise RuntimeError("Encryption key missing")
        cipher = AES.new(self._key, AES.MODE_CBC)
        ct = cipher.encrypt(pad(data_bytes, AES.block_size))
        iv_b64 = base64.b64encode(cipher.iv).decode("utf-8")
        ct_b64 = base64.b64encode(ct).decode("utf-8")
        return iv_b64, ct_b64

    def decrypt_data(self, iv_b64: str, ct_b64: str) -> bytes:
        if not self._key:
            raise RuntimeError("Encryption key missing")
        iv = base64.b64decode(iv_b64)
        ct = base64.b64decode(ct_b64)
        cipher = AES.new(self._key, AES.MODE_CBC, iv=iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt

    # ----------------- login UI -----------------
    def setup_login_ui(self):
        # clear frames
        for w in self.top_frame.winfo_children():
            w.destroy()
        for w in self.content_frame.winfo_children():
            w.destroy()

        title = tk.Label(self.content_frame, text="Fog Computing Encrypted Control System",
                         font=("Arial", 20, "bold"), bg="#f0f0f0")
        title.pack(pady=20)

        login_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        login_frame.pack(pady=20)

        tk.Label(login_frame, text="Username:", bg="#f0f0f0").grid(row=0, column=0, padx=8, pady=8)
        self.username_entry = tk.Entry(login_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(login_frame, text="Password:", bg="#f0f0f0").grid(row=1, column=0, padx=8, pady=8)
        self.password_entry = tk.Entry(login_frame, show="*", width=30)
        self.password_entry.grid(row=1, column=1, padx=8, pady=8)

        tk.Button(login_frame, text="Login", width=20, bg="#3498db", fg="white",
                  command=self.login).grid(row=2, column=0, columnspan=2, pady=12)

        # hint
        hint = tk.Label(self.content_frame, text="(Use: admin/admin123  or company/company123  or cloud/cloud123  or auditor/auditor123)",
                        bg="#f0f0f0")
        hint.pack(pady=6)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if username == "" or password == "":
            messagebox.showerror("Error", "Enter username and password")
            return

        hashed = self.hash_password(password)
        if username in self.users and self.users[username]["password"] == hashed:
            self.current_user = username
            self.audit_log.append({
                "user": username, "action": "login", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "success"
            })
            self.setup_main_ui()
        else:
            self.audit_log.append({
                "user": username, "action": "login", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "failed"
            })
            messagebox.showerror("Login failed", "Invalid credentials")

    # ----------------- main UI -----------------
    def setup_main_ui(self):
        # clear top and content
        for w in self.top_frame.winfo_children():
            w.destroy()
        for w in self.content_frame.winfo_children():
            w.destroy()

        # top nav buttons
        nav_frame = tk.Frame(self.top_frame, bg="#f0f0f0")
        nav_frame.pack(pady=6, padx=6, anchor="e")

        role = self.users.get(self.current_user, {}).get("role", "company")

        # buttons: map to methods or to file_ui
        btn_home = tk.Button(nav_frame, text="Home", width=12, bg="#3498db", fg="white", command=self.show_home)
        btn_home.grid(row=0, column=0, padx=4)

        # Upload, View Files are provided by file_ui
        btn_upload = tk.Button(nav_frame, text="Upload File", width=12, bg="#2ecc71", fg="white",
                               command=self.file_ui.upload_file)
        btn_upload.grid(row=0, column=1, padx=4)

        btn_view = tk.Button(nav_frame, text="View Files", width=12, bg="#f39c12", fg="white",
                             command=self.file_ui.view_files)
        btn_view.grid(row=0, column=2, padx=4)

        # some roles get extra buttons (you can expand these)
        if role == "administrator":
            # maybe admin-only actions in future
            pass

        btn_logout = tk.Button(nav_frame, text="Logout", width=10, bg="#e74c3c", fg="white",
                               command=self.logout)
        btn_logout.grid(row=0, column=10, padx=8)

        # Display logged-in info
        info = tk.Label(self.top_frame, text=f"Logged in as: {self.current_user} ({role})", bg="#f0f0f0")
        info.pack(side=tk.LEFT, padx=6)

        # default show home
        self.show_home()

    def show_home(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        tk.Label(self.content_frame, text="Home Page", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=20)
        desc = (
            "Secure Fog Computing Encrypted Control System\n\n"
            "• Encrypted File Management\n"
            "• Role-based access\n"
            "• Audit logs\n"
            "• Demonstration of fog-side encryption & local storage"
        )
        tk.Label(self.content_frame, text=desc, bg="#f0f0f0", justify=tk.LEFT).pack(padx=20, pady=10)

    def logout(self):
        self.current_user = None
        self.setup_login_ui()


if __name__ == "__main__":
    root = tk.Tk()
    app = FogApp(root)
    root.mainloop()
