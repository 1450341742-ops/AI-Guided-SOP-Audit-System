from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class KBItem:
    category: str
    title: str
    keywords: List[str]
    content: str


DEFAULT_KB: List[KBItem] = [
    KBItem(
        category="知情同意",
        title="知情同意证据链四问",
        keywords=["ICF", "知情", "签署", "伦理", "授权", "培训"],
        content="核查知情同意时，应确认版本有效性、签署时序、签署/解释人员授权培训、再知情触发与执行情况。",
    ),
    KBItem(
        category="入排标准",
        title="入排判断依据充分性",
        keywords=["入排", "筛选", "随机", "入组", "实验室", "影像"],
        content="入排标准核查不应只看EDC勾选结果，应追溯研究者作出判断前是否已掌握充分、有效、可追溯的原始依据。",
    ),
    KBItem(
        category="EDC一致性",
        title="EDC不一致的根因追溯",
        keywords=["EDC", "源文件", "Query", "一致", "审计追踪"],
        content="EDC与源文件不一致时，应追溯源数据、录入过程、Query处理、审计追踪和研究者审核，不宜简单归因为录入错误。",
    ),
    KBItem(
        category="AE/SAE",
        title="安全性事件核查提醒",
        keywords=["AE", "SAE", "安全性", "实验室异常", "上报"],
        content="AE/SAE核查需关注病历、实验室异常、合并用药、EDC记录和SAE上报记录的一致性。严重程度重不等于SAE。",
    ),
    KBItem(
        category="研究者文件夹",
        title="ISF不是归档柜",
        keywords=["研究者文件夹", "ISF", "授权", "培训", "伦理", "校准"],
        content="研究者文件夹用于证明中心具备合规执行条件，授权、培训、伦理、实验室、设备校准等均应形成执行依据证据链。",
    ),
]


def search_kb(text: str, limit: int = 3) -> List[Dict[str, str]]:
    text = text or ""
    scored = []
    for item in DEFAULT_KB:
        score = 0
        for kw in item.keywords:
            if re.search(re.escape(kw), text, re.IGNORECASE):
                score += 1
        if item.category in text:
            score += 2
        if score:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {"category": item.category, "title": item.title, "content": item.content}
        for _, item in scored[:limit]
    ]


def build_guidance_text(module: str, user_text: str) -> str:
    hits = search_kb(module + " " + user_text)
    if not hits:
        return "暂无匹配知识库提示。建议继续补充文件名称、日期、版本、人员、页码和源文件位置。"
    return "\n".join([f"【{h['category']}】{h['title']}：{h['content']}" for h in hits])
