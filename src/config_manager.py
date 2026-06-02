from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.guide_engine import DEFAULT_WORKFLOW

CONFIG_PATH = Path("workflow_config.json")


def load_workflow_config() -> List[Dict[str, Any]]:
    if not CONFIG_PATH.exists():
        return DEFAULT_WORKFLOW
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else DEFAULT_WORKFLOW
    except Exception:
        return DEFAULT_WORKFLOW


def save_workflow_config(workflow: List[Dict[str, Any]]) -> None:
    CONFIG_PATH.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")


def reset_workflow_config() -> None:
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()


def workflow_to_text(workflow: List[Dict[str, Any]]) -> str:
    return json.dumps(workflow, ensure_ascii=False, indent=2)


def text_to_workflow(text: str) -> List[Dict[str, Any]]:
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("配置必须是列表")
    return data
