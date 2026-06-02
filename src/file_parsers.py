from __future__ import annotations

from io import BytesIO
from typing import Dict, List

import pandas as pd

try:
    from docx import Document
except Exception:
    Document = None


def parse_uploaded_file(name: str, data: bytes) -> Dict[str, str]:
    lower = name.lower()
    if lower.endswith(".xlsx") or lower.endswith(".xls"):
        return parse_excel(data)
    if lower.endswith(".csv"):
        return parse_csv(data)
    if lower.endswith(".docx"):
        return parse_docx(data)
    if lower.endswith(".txt"):
        return {"type": "txt", "summary": data.decode("utf-8", errors="ignore")[:3000]}
    return {"type": "unknown", "summary": "当前版本仅支持xlsx、csv、docx、txt的文本级解析；图片和PDF可先保存文件名，后续接入OCR。"}


def parse_excel(data: bytes) -> Dict[str, str]:
    try:
        excel = pd.ExcelFile(BytesIO(data))
        lines: List[str] = []
        for sheet in excel.sheet_names[:10]:
            df = excel.parse(sheet, nrows=5)
            cols = [str(c) for c in df.columns]
            lines.append(f"Sheet：{sheet}；列名：" + "、".join(cols[:30]))
        return {"type": "excel", "summary": "\n".join(lines)}
    except Exception as exc:
        return {"type": "excel", "summary": f"Excel解析失败：{exc}"}


def parse_csv(data: bytes) -> Dict[str, str]:
    try:
        df = pd.read_csv(BytesIO(data), nrows=5)
        return {"type": "csv", "summary": "列名：" + "、".join([str(c) for c in df.columns[:50]])}
    except Exception as exc:
        return {"type": "csv", "summary": f"CSV解析失败：{exc}"}


def parse_docx(data: bytes) -> Dict[str, str]:
    if Document is None:
        return {"type": "docx", "summary": "当前环境未安装python-docx，无法解析docx。"}
    try:
        doc = Document(BytesIO(data))
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return {"type": "docx", "summary": text[:3000]}
    except Exception as exc:
        return {"type": "docx", "summary": f"Word解析失败：{exc}"}
