import json, time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
AUDIT_FILE = DATA_DIR / "audit_log.json"

def log(user, action, status="success", extra=None):
    rec = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "action": action,
        "status": status
    }
    if extra is not None:
        rec["extra"] = extra
    data = json.loads(AUDIT_FILE.read_text())
    data.append(rec)
    AUDIT_FILE.write_text(json.dumps(data, indent=2))

def get_logs():
    return json.loads(AUDIT_FILE.read_text())
