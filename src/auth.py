from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict

import streamlit as st


@dataclass
class User:
    username: str
    display_name: str
    role: str


# MVP本地账号。正式部署时建议改为数据库用户表、企业微信/飞书登录或Supabase Auth。
USERS: Dict[str, Dict[str, str]] = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode("utf-8")).hexdigest(),
        "display_name": "系统管理员",
        "role": "管理员",
    },
    "auditor": {
        "password_hash": hashlib.sha256("audit123".encode("utf-8")).hexdigest(),
        "display_name": "稽查员",
        "role": "稽查员",
    },
    "reviewer": {
        "password_hash": hashlib.sha256("review123".encode("utf-8")).hexdigest(),
        "display_name": "复核人",
        "role": "复核人",
    },
}

ROLE_PERMISSIONS = {
    "管理员": {"save", "create", "review", "config", "export", "view_log"},
    "稽查员": {"save", "create", "export"},
    "复核人": {"review", "export", "view_log"},
}


def login_box() -> bool:
    st.session_state.setdefault("user", None)
    if st.session_state.user:
        return True

    st.title("AI引导式稽查SOP执行系统")
    st.caption("请先登录。MVP默认账号：admin/admin123，auditor/audit123，reviewer/review123。")
    with st.form("login_form"):
        username = st.text_input("账号")
        password = st.text_input("密码", type="password")
        submitted = st.form_submit_button("登录")
    if submitted:
        user = USERS.get(username)
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if user and user["password_hash"] == password_hash:
            st.session_state.user = User(username=username, display_name=user["display_name"], role=user["role"])
            st.success("登录成功")
            st.rerun()
        else:
            st.error("账号或密码错误")
    return False


def logout_button() -> None:
    user = st.session_state.get("user")
    if not user:
        return
    st.sidebar.caption(f"当前用户：{user.display_name}｜{user.role}")
    if st.sidebar.button("退出登录", use_container_width=True):
        st.session_state.user = None
        st.rerun()


def has_permission(permission: str) -> bool:
    user = st.session_state.get("user")
    if not user:
        return False
    return permission in ROLE_PERMISSIONS.get(user.role, set())
