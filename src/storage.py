from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

# 从 Streamlit Secrets 中读取连接字符串
DB_URL = st.secrets["SUPABASE_DB_URL"]

def get_conn():
    # 连接 PostgreSQL，使用 RealDictCursor 确保返回的数据类型类似于字典
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)


def init_db() -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id SERIAL PRIMARY KEY,
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
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS step_inputs (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER NOT NULL,
                    step_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(project_id, step_id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS findings (
                    id SERIAL PRIMARY KEY,
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
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER,
                    action TEXT NOT NULL,
                    detail TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS uploaded_files (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER NOT NULL,
                    file_name TEXT NOT NULL,
                    file_type TEXT,
                    summary TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_files (
                    id SERIAL PRIMARY KEY,
                    kb_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_type TEXT,
                    summary TEXT,
                    tags TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                )
                """
            )
        conn.commit()
        
        # 补充缺失字段
        ensure_column("findings", "review_status", "TEXT DEFAULT '待复核'")
        ensure_column("findings", "review_comment", "TEXT DEFAULT ''")
        ensure_column("findings", "reviewer", "TEXT DEFAULT ''")
        ensure_column("findings", "reviewed_at", "TEXT DEFAULT ''")


def ensure_column(table: str, column: str, definition: str) -> None:
    # 针对 PostgreSQL 语法查询字段是否存在
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name=%s AND column_name=%s
                """,
                (table, column)
            )
            if not cur.fetchone():
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        conn.commit()


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_project(data: Dict[str, Any]) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO projects(project_name, sponsor, site_no, auditor, audit_type, subject_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
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
            project_id = cur.fetchone()['id']
            cur.execute(
                "INSERT INTO audit_logs(project_id, action, detail, created_at) VALUES (%s, %s, %s, %s)", 
                (project_id, "创建项目", json.dumps(data, ensure_ascii=False), now())
            )
        conn.commit()
        return project_id


def update_project(project_id: int, data: Dict[str, Any]) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE projects SET project_name=%s, sponsor=%s, site_no=%s, auditor=%s, audit_type=%s, subject_id=%s, updated_at=%s WHERE id=%s
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
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM projects ORDER BY updated_at DESC LIMIT %s", (limit,))
            rows = cur.fetchall()
    return [dict(row) for row in rows]


def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM projects WHERE id=%s", (project_id,))
            row = cur.fetchone()
    return dict(row) if row else None


def save_step_input(project_id: int, step_id: str, payload: Dict[str, Any]) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO step_inputs(project_id, step_id, payload, updated_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT(project_id, step_id) DO UPDATE SET payload=EXCLUDED.payload, updated_at=EXCLUDED.updated_at
                """,
                (project_id, step_id, json.dumps(payload, ensure_ascii=False), now()),
            )
            cur.execute(
                "INSERT INTO audit_logs(project_id, action, detail, created_at) VALUES (%s, %s, %s, %s)", 
                (project_id, "保存步骤", step_id, now())
            )
        conn.commit()


def load_step_inputs(project_id: int) -> Dict[str, Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT step_id, payload FROM step_inputs WHERE project_id=%s", (project_id,))
            rows = cur.fetchall()
    return {row["step_id"]: json.loads(row["payload"]) for row in rows}


def save_finding(project_id: int, payload: Dict[str, Any]) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO findings(project_id, payload, review_status, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
                (project_id, json.dumps(payload, ensure_ascii=False), "待复核", now()),
            )
            finding_id = cur.fetchone()['id']
            cur.execute(
                "INSERT INTO audit_logs(project_id, action, detail, created_at) VALUES (%s, %s, %s, %s)", 
                (project_id, "新增发现", payload.get("问题标题", ""), now())
            )
        conn.commit()
        return finding_id


def load_findings(project_id: int) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, payload, review_status, review_comment, reviewer, reviewed_at FROM findings WHERE project_id=%s ORDER BY id ASC", (project_id,))
            rows = cur.fetchall()
            
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
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE findings SET review_status=%s, review_comment=%s, reviewer=%s, reviewed_at=%s WHERE id=%s AND project_id=%s",
                (status, comment, reviewer, now(), finding_id, project_id),
            )
            cur.execute(
                "INSERT INTO audit_logs(project_id, action, detail, created_at) VALUES (%s, %s, %s, %s)", 
                (project_id, "复核发现", f"ID={finding_id}; 状态={status}", now())
            )
        conn.commit()


def save_uploaded_file_summary(project_id: int, file_name: str, file_type: str, summary: str) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO uploaded_files(project_id, file_name, file_type, summary, created_at) VALUES (%s, %s, %s, %s, %s)",
                (project_id, file_name, file_type, summary, now()),
            )
            cur.execute(
                "INSERT INTO audit_logs(project_id, action, detail, created_at) VALUES (%s, %s, %s, %s)", 
                (project_id, "解析文件", file_name, now())
            )
        conn.commit()


def load_uploaded_files(project_id: int) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM uploaded_files WHERE project_id=%s ORDER BY id DESC", (project_id,))
            rows = cur.fetchall()
    return [dict(row) for row in rows]


def save_knowledge_file(kb_name: str, category: str, file_name: str, file_type: str, summary: str, tags: str = "") -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO knowledge_files(kb_name, category, file_name, file_type, summary, tags, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (kb_name or "公司知识库", category or "未分类", file_name, file_type, summary, tags, now()),
            )
            cur.execute(
                "INSERT INTO audit_logs(project_id, action, detail, created_at) VALUES (%s, %s, %s, %s)", 
                (None, "上传知识库", f"{kb_name}/{category}/{file_name}", now())
            )
        conn.commit()


def load_knowledge_files(keyword: str = "", category: str = "") -> List[Dict[str, Any]]:
    query = "SELECT * FROM knowledge_files WHERE 1=1"
    params: List[Any] = []
    
    if keyword:
        # PostgreSQL 的 ILIKE 用于不区分大小写的匹配
        query += " AND (file_name ILIKE %s OR summary ILIKE %s OR tags ILIKE %s OR kb_name ILIKE %s)"
        like = f"%{keyword}%"
        params.extend([like, like, like, like])
        
    if category and category != "全部":
        query += " AND category=%s"
        params.append(category)
        
    query += " ORDER BY id DESC LIMIT 300"
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
    return [dict(row) for row in rows]


def list_knowledge_categories() -> List[str]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT category FROM knowledge_files ORDER BY category")
            rows = cur.fetchall()
    return [row["category"] for row in rows]


def load_logs(project_id: Optional[int] = None) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            if project_id:
                cur.execute("SELECT * FROM audit_logs WHERE project_id=%s ORDER BY id DESC LIMIT 100", (project_id,))
            else:
                cur.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 100")
            rows = cur.fetchall()
    return [dict(row) for row in rows]
