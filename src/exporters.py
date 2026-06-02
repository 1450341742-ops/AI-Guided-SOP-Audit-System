from __future__ import annotations

from io import BytesIO
from typing import Dict, List

import pandas as pd

from src.capa import build_capa_items


def build_excel_package(findings: List[Dict[str, str]], logs: List[Dict[str, str]] | None = None) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        findings_df = pd.DataFrame(findings) if findings else pd.DataFrame(columns=["问题分类", "问题标题", "问题描述", "风险等级", "建议措施"])
        findings_df.to_excel(writer, index=False, sheet_name="问题清单")
        capa_df = pd.DataFrame(build_capa_items(findings)) if findings else pd.DataFrame(columns=["问题分类", "根因分析方向", "纠正措施", "预防措施", "完成期限"])
        capa_df.to_excel(writer, index=False, sheet_name="CAPA计划")
        if logs:
            pd.DataFrame(logs).to_excel(writer, index=False, sheet_name="操作日志")
        summary_rows = [
            {"指标": "发现问题数量", "数值": len(findings)},
            {"指标": "高风险数量", "数值": sum(1 for x in findings if x.get("风险等级") == "高")},
            {"指标": "中风险数量", "数值": sum(1 for x in findings if x.get("风险等级") == "中")},
            {"指标": "低风险数量", "数值": sum(1 for x in findings if x.get("风险等级") == "低")},
        ]
        pd.DataFrame(summary_rows).to_excel(writer, index=False, sheet_name="统计摘要")
    output.seek(0)
    return output.getvalue()
