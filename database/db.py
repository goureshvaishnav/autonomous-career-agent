"""SQLite persistence for student profiles and roadmap progress."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "career_agent.db"

def get_connection(db_path: str | Path | None = None):
    path = Path(db_path) if db_path else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str | Path | None = None):
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                education TEXT,
                skills_json TEXT,
                interests_json TEXT,
                goal TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS roadmap_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT NOT NULL,
                career_title TEXT NOT NULL,
                week INTEGER NOT NULL,
                skill TEXT NOT NULL,
                task TEXT NOT NULL,
                resource TEXT,
                url TEXT,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_profile(profile: dict, db_path: str | Path | None = None):
    init_db(db_path)
    with get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO profiles (name, education, skills_json, interests_json, goal, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            profile.get("name", "Student"),
            profile.get("education", ""),
            json.dumps(profile.get("skills", [])),
            json.dumps(profile.get("interests", [])),
            profile.get("goal", ""),
        ))

def replace_roadmap(profile_name: str, career_title: str, roadmap, db_path: str | Path | None = None):
    init_db(db_path)
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM roadmap_tasks WHERE profile_name = ?", (profile_name,))
        for _, row in roadmap.iterrows():
            conn.execute("""
                INSERT INTO roadmap_tasks (profile_name, career_title, week, skill, task, resource, url, completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                profile_name, career_title, int(row["week"]), str(row["skill"]),
                str(row["task"]), str(row.get("resource", "")), str(row.get("url", "")),
            ))

def get_tasks(profile_name: str, db_path: str | Path | None = None):
    init_db(db_path)
    with get_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM roadmap_tasks WHERE profile_name = ? ORDER BY week, id",
            (profile_name,)
        ).fetchall()

def set_task_completed(task_id: int, completed: bool, db_path: str | Path | None = None):
    with get_connection(db_path) as conn:
        conn.execute("UPDATE roadmap_tasks SET completed = ? WHERE id = ?", (int(completed), int(task_id)))
