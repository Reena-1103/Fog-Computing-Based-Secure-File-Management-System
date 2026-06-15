# ui/file_ui.py
# Provides FileUI class used by the main application.
# Paste this file into ui/file_ui.py (replace existing).

import os
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class FileUI:
    """
    FileUI is a helper class that attaches to your main application instance.
    The main app should do something like:
        from ui.file_ui import FileUI
        self.file_ui = FileUI(self)
    The FileUI methods use self.app to call encryption helpers:
        self.app.encrypt_data(bytes) -> (iv_base64, ct_base64)
        self.app.decrypt_data(iv_base64, ct_base64) -> bytes
    The main app should also have:
        - self.content_frame : a tk.Frame used to display content
        - self.current_user : currently logged-in username
        - optionally: self.files, self.audit_log lists/dicts
    """

    def __init__(self, app):
        self.app = app
        # content_frame must exist on the app; if not, try to create one
        if hasattr(app, "content_frame"):
            self.content_frame = app.content_frame
        else:
            # create a frame on app.root if available
            if hasattr(app, "root"):
                self.content_frame = tk.Frame(app.root, bg="#f0f0f0")
                self.content_frame.pack(fill=tk.BOTH, expand=True)
                app.content_frame = self.content_frame
            else:
                raise RuntimeError("App does not provide content_frame or root. FileUI cannot attach.")

    # ---------------- UI: Upload ----------------
    def upload_file(self):
        """Show upload UI with Browse + Upload buttons."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="Upload File", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        file_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        file_frame.pack(pady=10)

        tk.Label(file_frame, text="Select File:", bg="#f0f0f0").grid(row=0, column=0)
        self.file_path = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.file_path, width=50).grid(row=0, column=1, padx=6)

        tk.Button(file_frame, text="Browse", command=self.browse_file, bg="#3498db", fg="white").grid(row=0, column=2, padx=6)
        tk.Button(self.content_frame, text="Upload", command=self.process_upload, bg="#2ecc71", fg="white").pack(pady=12)

    def browse_file(self):
        """Open file dialog and set the chosen path into the entry."""
        filename = filedialog.askopenfilename(title="Select File")
        if filename:
            self.file_path.set(filename)

    def process_upload(self):
        """Encrypt the selected file and save metadata JSON in data/files/."""
        filepath = getattr(self, "file_path", tk.StringVar()).get()
        if not filepath:
            messagebox.showerror("Error", "Select a file to upload.")
            return

        try:
            with open(filepath, "rb") as f:
                raw = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")
            return

        # call encryption helper on the main app
        if not hasattr(self.app, "encrypt_data"):
            messagebox.showerror("Error", "Encryption function not available on app.")
            return

        try:
            iv, ct = self.app.encrypt_data(raw)  # both expected to be base64 strings
            import textwrap
            ct = "\n".join(textwrap.wrap(ct, 80))
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed: {e}")
            return

        os.makedirs(os.path.join("data", "files"), exist_ok=True)
        fname = os.path.basename(filepath)
        meta = {
            "original_name": fname,
            "stored_name": fname + ".enc.json",
            "uploaded_by": getattr(self.app, "current_user", "unknown"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "iv": iv,
            "content": ct
        }
        savepath = os.path.join("data", "files", meta["stored_name"])
        try:
            with open(savepath, "w", encoding="utf-8") as mf:
                json.dump(meta, mf, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save encrypted file: {e}")
            return

        # update app memory structures if available
        try:
            if hasattr(self.app, "files") and isinstance(self.app.files, dict):
                self.app.files[meta["original_name"]] = meta
            if hasattr(self.app, "audit_log") and isinstance(self.app.audit_log, list):
                self.app.audit_log.append({
                    "user": getattr(self.app, "current_user", "unknown"),
                    "action": f"upload_file:{meta['original_name']}",
                    "timestamp": meta["timestamp"],
                    "status": "success"
                })
        except Exception:
            pass

        messagebox.showinfo("Success", f"File '{fname}' uploaded and encrypted.")
        # optional: refresh view
        self.view_files()

    # ---------------- UI: View / Download ----------------
    def view_files(self):
        """List encrypted files (reads JSON meta files from data/files)."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="Encrypted Files", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=8)

        cols = ("Filename", "Uploaded By", "Timestamp")
        tree = ttk.Treeview(self.content_frame, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=220)

        tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        data_dir = os.path.join("data", "files")
        if not os.path.exists(data_dir):
            tk.Label(self.content_frame, text="No files found.", bg="#f0f0f0").pack()
            return

        files_meta = []
        for fname in sorted(os.listdir(data_dir)):
            if not fname.lower().endswith(".json"):
                continue
            try:
                with open(os.path.join(data_dir, fname), "r", encoding="utf-8") as mf:
                    obj = json.load(mf)
                    files_meta.append(obj)
            except Exception:
                continue

        for fm in files_meta:
            tree.insert("", "end", values=(fm.get("original_name"), fm.get("uploaded_by"), fm.get("timestamp")))

        btn_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Upload File", command=self.upload_file, bg="#2ecc71", fg="white").grid(row=0, column=0, padx=6)
        tk.Button(btn_frame, text="Download Selected", command=lambda: self.download_file(tree), bg="#3498db", fg="white").grid(row=0, column=1, padx=6)
        if not self.app.has_permission("download"):
            messagebox.showerror("Access Denied", "You cannot download files")
            return

    def download_file(self, tree):
        """Decrypt the selected file and ask user where to save it."""
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error", "Select a file to download.")
            return

        original_name = tree.item(sel[0])["values"][0]
        data_dir = os.path.join("data", "files")
        meta_obj = None
        for f in os.listdir(data_dir):
            if f.lower().endswith(".json"):
                try:
                    with open(os.path.join(data_dir, f), "r", encoding="utf-8") as mf:
                        obj = json.load(mf)
                        if obj.get("original_name") == original_name:
                            meta_obj = obj
                            break
                except Exception:
                    continue

        if not meta_obj:
            messagebox.showerror("Error", "Metadata for selected file not found.")
            return

        iv = meta_obj.get("iv")
        ct = meta_obj.get("content").replace("\n", "")
        if not (iv and ct):
            messagebox.showerror("Error", "Invalid stored file.")
            return

        if not hasattr(self.app, "decrypt_data"):
            messagebox.showerror("Error", "Decrypt function not available on app.")
            return

        try:
            if not self.app.has_permission("decrypt"):
                messagebox.showerror("Access Denied", "You cannot decrypt files")
                return
            from tkinter import simpledialog
            pwd = simpledialog.askstring("Security Check", "Enter decryption password:", show="*")
            if pwd != "secure@123":
                messagebox.showerror("Access Denied", "Wrong decryption password")
                return
            plaintext = self.app.decrypt_data(iv, ct)  # expected to return bytes
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {e}")
            return

        save_to = filedialog.asksaveasfilename(title="Save Decrypted File As", initialfile=meta_obj.get("original_name","downloaded.bin"))
        if not save_to:
            return

        try:
            with open(save_to, "wb") as out:
                out.write(plaintext)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
            return

        # log
        try:
            if hasattr(self.app, "audit_log") and isinstance(self.app.audit_log, list):
                self.app.audit_log.append({
                    "user": getattr(self.app, "current_user", "unknown"),
                    "action": f"download_file:{meta_obj.get('original_name')}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "success"
                })
        except Exception:
            pass

        messagebox.showinfo("Success", f"File saved to: {save_to}")
