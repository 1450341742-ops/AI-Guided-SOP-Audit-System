from __future__ import annotations

from io import BytesIO
from typing import Dict, List

import pandas as pd

try:
    from docx import Document
except Exception:
    Document = None

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

try:
    from pptx import Presentation
except Exception:
    Presentation = None

try:
    from PIL import Image
except Exception:
    Image = None


def parse_uploaded_file(name: str, data: bytes) -> Dict[str, str]:
    lower = name.lower()
    if lower.endswith(".xlsx") or lower.endswith(".xls"):
        return parse_excel(data)
    if lower.endswith(".csv"):
        return parse_csv(data)
    if lower.endswith(".docx"):
        return parse_docx(data)
    if lower.endswith(".pdf"):
        return parse_pdf(data)
    if lower.endswith(".pptx"):
        return parse_pptx(data)
    if lower.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp")):
        return parse_image(data)
    if lower.endswith(".txt"):
        return {"type": "txt", "summary": data.decode("utf-8", errors="ignore")[:5000]}
    return {"type": "unknown", "summary": "暂不支持该文件类型。建议转换为Word、PDF、Excel、PPT、图片或TXT后上传。"}


def parse_excel(data: bytes) -> Dict[str, str]:
    try:
        excel = pd.ExcelFile(BytesIO(data))
        lines: List[str] = []
        for sheet in excel.sheet_names[:15]:
            df = excel.parse(sheet, nrows=8)
            cols = [str(c) for c in df.columns]
            sample = df.head(2).fillna("").astype(str).to_dict(orient="records")
            lines.append(f"Sheet：{sheet}\n列名：" + "、".join(cols[:50]) + f"\n样例：{sample}")
        return {"type": "excel", "summary": "\n\n".join(lines)[:9000]}
    except Exception as exc:
        return {"type": "excel", "summary": f"Excel解析失败：{exc}"}


def parse_csv(data: bytes) -> Dict[str, str]:
    try:
        df = pd.read_csv(BytesIO(data), nrows=8)
        sample = df.head(3).fillna("").astype(str).to_dict(orient="records")
        return {"type": "csv", "summary": ("列名：" + "、".join([str(c) for c in df.columns[:80]]) + f"\n样例：{sample}")[:9000]}
    except Exception as exc:
        return {"type": "csv", "summary": f"CSV解析失败：{exc}"}


def parse_docx(data: bytes) -> Dict[str, str]:
    if Document is None:
        return {"type": "docx", "summary": "当前环境未安装python-docx，无法解析docx。"}
    try:
        doc = Document(BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        table_lines: List[str] = []
        for table in doc.tables[:5]:
            for row in table.rows[:8]:
                table_lines.append(" | ".join(cell.text.strip() for cell in row.cells[:8]))
        text = "\n".join(paragraphs + table_lines)
        return {"type": "docx", "summary": text[:9000]}
    except Exception as exc:
        return {"type": "docx", "summary": f"Word解析失败：{exc}"}


def parse_pdf(data: bytes) -> Dict[str, str]:
    if PdfReader is None:
        return {"type": "pdf", "summary": "当前环境未安装PyPDF2，无法解析PDF文本。"}
    try:
        reader = PdfReader(BytesIO(data))
        parts: List[str] = []
        for i, page in enumerate(reader.pages[:20], start=1):
            text = page.extract_text() or ""
            if text.strip():
                parts.append(f"第{i}页：\n{text[:1200]}")
        summary = "\n\n".join(parts)
        if not summary.strip():
            summary = "PDF未提取到文本，可能是扫描件。当前版本可保存文件信息，后续需接入OCR。"
        return {"type": "pdf", "summary": summary[:12000]}
    except Exception as exc:
        return {"type": "pdf", "summary": f"PDF解析失败：{exc}"}


def parse_pptx(data: bytes) -> Dict[str, str]:
    if Presentation is None:
        return {"type": "pptx", "summary": "当前环境未安装python-pptx，无法解析PPT。"}
    try:
        prs = Presentation(BytesIO(data))
        lines: List[str] = []
        for idx, slide in enumerate(prs.slides[:30], start=1):
            texts: List[str] = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    texts.append(shape.text.strip())
            if texts:
                lines.append(f"第{idx}页：" + "；".join(texts[:12]))
        return {"type": "pptx", "summary": "\n".join(lines)[:10000]}
    except Exception as exc:
        return {"type": "pptx", "summary": f"PPT解析失败：{exc}"}


def parse_image(data: bytes) -> Dict[str, str]:
    if Image is None:
        return {"type": "image", "summary": "当前环境未安装Pillow，无法读取图片信息。"}
    try:
        img = Image.open(BytesIO(data))
        return {"type": "image", "summary": f"图片文件，格式：{img.format}，尺寸：{img.size[0]}x{img.size[1]}。当前版本保存图片元数据，图片文字识别需后续接入OCR。"}
    except Exception as exc:
        return {"type": "image", "summary": f"图片解析失败：{exc}"}
