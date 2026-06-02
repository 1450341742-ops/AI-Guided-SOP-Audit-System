from dataclasses import dataclass, field
from typing import List

@dataclass
class RuleResult:
    risk_level: str
    summary: str
    questions: List[str] = field(default_factory=list)
    triggered_rules: List[str] = field(default_factory=list)
    need_finding: bool = False

@dataclass
class AuditRecord:
    project_name: str
    site_no: str
    subject_id: str
    module: str
    issue_title: str
    issue_description: str
    evidence: str
    risk_level: str
    risk_impact: str
    recommendation: str
    status: str = "待稽查员确认"
