import sqlite3
from pathlib import Path
import json

DB_PATH = Path(__file__).resolve().parents[1] / "english_mastery.db"

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_type TEXT NOT NULL,
            question_text TEXT NOT NULL,
            user_answer TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            marks_awarded REAL NOT NULL,
            max_marks REAL NOT NULL,
            explanation TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS writing_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            writing_type TEXT NOT NULL,
            prompt TEXT,
            submitted_text TEXT NOT NULL,
            score REAL NOT NULL,
            max_marks REAL NOT NULL,
            feedback_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS question_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_type TEXT NOT NULL,
            question_text TEXT NOT NULL,
            normalized_text TEXT NOT NULL UNIQUE,
            answer TEXT,
            explanation TEXT
        );
        """)

def save_attempt(question_type, question_text, user_answer, correct_answer, marks_awarded, max_marks, explanation=""):
    from modules.duplicates import normalize_text
    with connect() as con:
        con.execute(
            """INSERT INTO attempts
            (question_type, question_text, user_answer, correct_answer, marks_awarded, max_marks, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (question_type, question_text, user_answer, correct_answer, marks_awarded, max_marks, explanation)
        )
        normalized = normalize_text(question_text)
        try:
            con.execute(
                """INSERT INTO question_bank (question_type, question_text, normalized_text, answer, explanation)
                VALUES (?, ?, ?, ?, ?)""",
                (question_type, question_text, normalized, correct_answer, explanation)
            )
        except sqlite3.IntegrityError:
            pass

def save_writing(writing_type, prompt, submitted_text, score, max_marks, feedback):
    with connect() as con:
        con.execute(
            """INSERT INTO writing_submissions
            (writing_type, prompt, submitted_text, score, max_marks, feedback_json)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (writing_type, prompt, submitted_text, score, max_marks, json.dumps(feedback, ensure_ascii=False))
        )

def get_stats():
    with connect() as con:
        attempts = con.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
        correct = con.execute("SELECT COUNT(*) FROM attempts WHERE marks_awarded >= max_marks").fetchone()[0]
        writings = con.execute("SELECT COUNT(*) FROM writing_submissions").fetchone()[0]
    return {"objective_attempts": attempts, "correct_answers": correct, "writing_submissions": writings}

def get_recent_attempts(limit=50):
    with connect() as con:
        rows = con.execute(
            """SELECT created_at, question_type, question_text, user_answer, correct_answer,
            marks_awarded, max_marks, explanation FROM attempts ORDER BY id DESC LIMIT ?""", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]

def get_writings(limit=20):
    with connect() as con:
        rows = con.execute(
            """SELECT created_at, writing_type, prompt, submitted_text, score, max_marks, feedback_json
            FROM writing_submissions ORDER BY id DESC LIMIT ?""", (limit,)
        ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["feedback"] = "; ".join(json.loads(item.pop("feedback_json")))
        item["submitted_text"] = item["submitted_text"][:350] + ("…" if len(item["submitted_text"]) > 350 else "")
        out.append(item)
    return out
