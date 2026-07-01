import json
import os
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(os.getenv("DATABASE_URL", Path(__file__).parent / "talentlens.db"))


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs_cache (
            query TEXT NOT NULL,
            location TEXT NOT NULL,
            jobs_json TEXT NOT NULL,
            fetched_at INTEGER NOT NULL,
            PRIMARY KEY (query, location)
        )
        """
    )
    conn.commit()
    conn.close()


def save_jobs(query: str, location: str, jobs: list):
    init_db()
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO jobs_cache (query, location, jobs_json, fetched_at) VALUES (?, ?, ?, ?)",
        (query, location, json.dumps(jobs), int(time.time())),
    )
    conn.commit()
    conn.close()


def load_jobs(query: str, location: str):
    init_db()
    conn = _connect()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT jobs_json, fetched_at FROM jobs_cache WHERE query = ? AND location = ?",
        (query, location),
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {"jobs": json.loads(row["jobs_json"]), "fetched_at": row["fetched_at"]}
