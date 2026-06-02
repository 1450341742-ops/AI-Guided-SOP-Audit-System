from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path("audit_system.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                sponsor TEXT,
                site_no TEXT,
                auditor TEXT,
                audit_type TEXT,
                subject_id TEXT,
                status TEXT DEFAULT '进行中',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS step_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                step_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(project_id, step_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                payload TEXT NOT NULL,
                review_status TEXT DEFAULT '待复核',
                review_comment TEXT DEFAULT '',
                reviewer TEXT DEFAULT '',
                reviewed_at TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                action TEXT NOT NULL,
                detail TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS uploaded_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT,
                summary TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        ensure_column(conn, "findings", "review_status", "TEXT DEFAULT '待复核'")
        ensure_column(conn, "findings", "review_comment", "TEXT DEFAULT ''")
        ensure_column(conn, "findings", "reviewer", "TEXT DEFAULT ''")
        ensure_column(conn, "findings", "reviewed_at", "TEXT DEFAULT ''")
        conn.commit()


def ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_project(data: Dict[str, Any]) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO projects(project_name, sponsor, site_no, auditor, audit_type, subject_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("project_name") or "未命名项目",
                data.get("sponsor", ""),
                data.get("site_no", ""),
                data.get("auditor", ""),
                data.get("audit_type", ""),
                data.get("subject_id", ""),
                now(),
                now(),
            ),
        )
        project_id = int(cur.lastrowid)
        conn.execute("INSERT INTO audit_logs(project_id, action, detail, created_at) VALUES (?, ?, ?, ?)", (project_id, "创建项目", json.dumps(data, ensure_ascii=False), now()))
        conn.commit()
        return project_id


def update_project(project_id: int, data: Dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE projects SET project_name=?, sponsor=?, site_no=?, auditor=?, audit_type=?, subject_id=?, updated_at=? WHERE id=?
            """,
            (
                data.get("project_name") or "未命名项目",
                data.get("sponsor", ""),
                data.get("site_no", ""),
                data.get("auditor", ""),
                data.get("audit_type", ""),
                data.get("subject_id", ""),
                now(),
                project_id,
            ),
        )
        conn.commit()


def list_projects(limit: int = 50) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM projects ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]


def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    return dict(row) if row else None


def save_step_input(project_id: int, step_id: str, payload: Dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO step_inputs(project_id, step_id, payload, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(project_id, step_id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at
            """,
            (project_id, step_id, json.dumps(payload, ensure_ascii=False), now()),
        )
        conn.execute("INSERT INTO audit_logs(project_id, action, detail, created_at) VALUES (?, ?, ?, ?)", (project_id, "保存步骤", step_id, now()))
        conn.commit()


def load_step_inputs(project_id: int) -> Dict[str, Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT step_id, payload FROM step_inputs WHERE project_id=?", (project_id,)).fetchall()
    return {row["step_id"]: json.loads(row["payload"]) for row in rows}


def save_finding(project_id: int, payload: Dict[str, Any]) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO findings(project_id, payload, review_status, created_at) VALUES (?, ?, ?, ?)",
            (project_id, json.dumps(payload, ensure_ascii=False), "待复核", now()),
        )
        conn.execute("INSERT INTO audit_logs(project_id, action, detail, created_at) VALUES (?, ?, ?, ?)", (project_id, "新增发现", payload.get("问题标题", ""), now()))
        conn.commit()
        return int(cur.lastrowid)


def load_findings(project_id: int) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT id, payload, review_status, review_comment, reviewer, reviewed_at FROM findings WHERE project_id=? ORDER BY id ASC", (project_id,)).fetchall()
    result: List[Dict[str, Any]] = []
    for row in rows:
        payload = json.loads(row["payload"])
        payload["记录ID"] = row["id"]
        payload["复核状态"] = row["review_status"]
        payload["复核意见"] = row["review_comment"]
        payload["复核人"] = row["reviewer"]
        payload["复核时间"] = row["reviewed_at"]
        result.append(payload)
    return result


def update_finding_review(project_id: int, finding_id: int, status: str, comment: str, reviewer: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE findings SET review_status=?, review_comment=?, reviewer=?, reviewed_at=? WHERE id=? AND project_id=?",
            (status, comment, reviewer, now(), finding_id, project_id),
        )
        conn.execute("INSERT INTO audit_logs(project_id, action, detail, created_at) VALUES (?, ?, ?, ?)", (project_id, "复核发现", f"ID={finding_id}; 状态={status}", now()))
        conn.commit()


def save_uploaded_file_summary(project_id: int, file_name: str, file_type: str, summary: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO uploaded_files(project_id, file_name, file_type, summary, created_at) VALUES (?, ?, ?, ?, ?)",
            (project_id, file_name, file_type, summary, now()),
        )
        conn.execute("INSERT INTO audit_logs(project_id, action, detail, created_at) VALUES (?, ?, ?, ?)", (project_id, "解析文件", file_name, now()))
        conn.commit()


def load_uploaded_files(project_id: int) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM uploaded_files WHERE project_id=? ORDER BY id DESC", (project_id,)).fetchall()
    return [dict(row) for row in rows]


def load_logs(project_id: Optional[int] = None) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        if project_id:
            rows = conn.execute("SELECT * FROM audit_logs WHERE project_id=? ORDER BY id DESC LIMIT 100", (project_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 100").fetchall()
    return [dict(row) for row in rows]
