import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List

DB_PATH = Path(__file__).parent / "users.db"


def init_db():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id       TEXT PRIMARY KEY,
                name          TEXT DEFAULT '',
                profession    TEXT DEFAULT '',
                domains       TEXT DEFAULT '[]',
                delivery_time TEXT DEFAULT '07:00',
                timezone      TEXT DEFAULT 'Asia/Kolkata',
                active        INTEGER DEFAULT 1,
                onboarding_step TEXT DEFAULT 'START',
                last_briefed_date TEXT DEFAULT '',
                created_at    TEXT
            )
        """)


def _conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _to_dict(row) -> Optional[dict]:
    if not row:
        return None
    d = dict(row)
    d["domains"] = json.loads(d.get("domains") or "[]")
    d["active"] = bool(d.get("active", 1))
    return d


def get_user(user_id: str) -> Optional[dict]:
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    return _to_dict(row)


def upsert_user(user_id: str, **fields):
    existing = get_user(user_id)
    if existing:
        parts, vals = [], []
        for k, v in fields.items():
            if k == "domains":
                v = json.dumps(v)
            elif k == "active":
                v = 1 if v else 0
            parts.append(f"{k} = ?")
            vals.append(v)
        vals.append(user_id)
        with _conn() as c:
            c.execute(f"UPDATE users SET {', '.join(parts)} WHERE user_id = ?", vals)
    else:
        fields["user_id"] = user_id
        fields.setdefault("created_at", datetime.now().isoformat())
        fields.setdefault("onboarding_step", "START")
        fields.setdefault("active", True)
        fields.setdefault("domains", [])
        if "domains" in fields:
            fields["domains"] = json.dumps(fields["domains"])
        if "active" in fields:
            fields["active"] = 1 if fields["active"] else 0
        cols = ", ".join(fields.keys())
        placeholders = ", ".join(["?"] * len(fields))
        with _conn() as c:
            c.execute(f"INSERT INTO users ({cols}) VALUES ({placeholders})", list(fields.values()))


def get_all_active_users() -> List[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM users WHERE active = 1 AND onboarding_step = 'COMPLETE'"
        ).fetchall()
    return [_to_dict(r) for r in rows]


def mark_briefed_today(user_id: str):
    upsert_user(user_id, last_briefed_date=datetime.now().strftime("%Y-%m-%d"))


def already_briefed_today(user: dict) -> bool:
    return user.get("last_briefed_date") == datetime.now().strftime("%Y-%m-%d")
