import os
import json
import tempfile
import threading
from functools import wraps
from app.core.config import settings

_lock = threading.Lock()
FILE = settings.DATA_FILE
os.makedirs(os.path.dirname(FILE) or ".", exist_ok=True)

def with_lock(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        with _lock:
            return fn(*args, **kwargs)
    return wrapper

@with_lock
def load():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@with_lock
def save(data):
    directory = os.path.dirname(FILE) or "."
    fd, tmp = tempfile.mkstemp(prefix="db_", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, FILE)  # escritura atómica
    finally:
        try:
            os.remove(tmp)
        except FileNotFoundError:
            pass
