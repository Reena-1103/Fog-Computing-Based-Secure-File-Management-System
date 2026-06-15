import tkinter as tk
from tkinter import ttk, messagebox
from ui.file_ui import FileUI
from core.audit import get_logs

class Dashboard:
    def __init__(self, root, auth):
        self.root = root
        self.auth = auth
        self.content = tk.Frame(self.root, bg="#f8f9fb")
        self.content.pack(fill="both", expand=True)
        header = tk.Frame(self.content, bg="#2c3e50")
        header.pack(fill="x")
        tk.Label(header, text="Fog Computing Encrypted Control System", fg="white", bg="#2c3e50", font=("Arial", 16, "bold")).pack(side="left", padx=12, pady=10)
        tk.Label(header, text=f"Logged in as: {auth['username']} ({auth['role']})", fg="white", bg="#2c3e50").pack(side="right", padx=12)

        # Menu
        menu = tk.Frame(self.content, bg="#ecf0f1"); menu.pack(fill="x", pady=8)
        buttons = [("Home", self.show_home), ("Upload / Files", self.show_files)]
        if self.auth["role"] in ("administrator","cloud","auditor"):
            buttons.append(("Audit Log", self.show_audit))
        buttons.append(("Logout", self.logout))
        for i,(txt,cmd) in enumerate(buttons):
            tk.Button(menu, text=txt, command=cmd, bg=["#3498db","#2ecc71","#9b59b6","#e74c3c"][i%4], fg="white", width=16).pack(side="left", padx=6, pady=6)

        # Work area
        self.body = tk.Frame(self.content, bg="#f8f9fb"); self.body.pack(fill="both", expand=True)
        self.show_home()

    def clear_body(self):
        for w in self.body.winfo_children():
            w.destroy()

    def show_home(self):
        self.clear_body()
        tk.Label(self.body, text="Home", font=("Arial", 14, "bold"), bg="#f8f9fb").pack(pady=10)
        desc = "Secure Fog Computing System\n• Encrypted File Management\n• Role-Based Access\n• Audit Logging"
        tk.Label(self.body, text=desc, bg="#f8f9fb").pack(pady=6)

    def show_files(self):
        self.clear_body()
        FileUI(self.body, self.auth)

    def show_audit(self):
        self.clear_body()
        tk.Label(self.body, text="Audit Log", font=("Arial", 14, "bold"), bg="#f8f9fb").pack(pady=10)
        tree = ttk.Treeview(self.body, columns=("timestamp","user","action","status"), show="headings")
        for c in ("timestamp","user","action","status"):
            tree.heading(c, text=c.title()); tree.column(c, width=180)
        for rec in get_logs():
            tree.insert("", "end", values=(rec.get("timestamp"),rec.get("user"),rec.get("action"),rec.get("status")))
        tree.pack(fill="both", expand=True, padx=12, pady=12)

    def logout(self):
        messagebox.showinfo("Logout", "Please close and re-run the application to login again.")
        self.root.destroy()
