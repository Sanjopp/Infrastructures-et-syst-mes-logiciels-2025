import json
from dataclasses import asdict
from pathlib import Path

from backend.models.auth_user import AuthUser

DATA_FILE = Path("data/users.json")


def load_users():
    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        return []
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return [AuthUser(**u) for u in data]
    except (json.JSONDecodeError, FileNotFoundError, TypeError):
        return []


def save_users(users):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump([asdict(u) for u in users], f, indent=2)
