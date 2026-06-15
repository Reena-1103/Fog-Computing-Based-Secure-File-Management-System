import tkinter as tk
from tkinter import messagebox
from core.users import authenticate
from core.audit import log
from ui.dashboard_ui import Dashboard

class LoginUI:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root, bg="#f0f0f0")
        self.frame.pack(fill="both", expand=True)
        tk.Label(self.frame, text="Fog Computing Encrypted Control System", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=20)
        form = tk.Frame(self.frame, bg="#f0f0f0")
        form.pack(pady=10)
        tk.Label(form, text="Username:", bg="#f0f0f0").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        tk.Label(form, text="Password:", bg="#f0f0f0").grid(row=1, column=0, padx=8, pady=8, sticky="e")
        self.u = tk.Entry(form, width=30); self.u.grid(row=0, column=1, padx=8, pady=8)
        self.p = tk.Entry(form, show="*", width=30); self.p.grid(row=1, column=1, padx=8, pady=8)
        tk.Button(self.frame, text="Login", bg="#3498db", fg="white", width=16, command=self.login).pack(pady=14)

    def login(self):
        user = self.u.get().strip(); pw = self.p.get().strip()
        if not user or not pw:
            messagebox.showerror("Error", "Enter username and password")
            return
        auth = authenticate(user, pw)
        if auth:
            log(user, "login", "success")
            self.frame.destroy()
            Dashboard(self.root, auth)
        else:
            log(user, "login", "failed")
            messagebox.showerror("Error", "Invalid credentials")
