from __future__ import annotations

from typing import Dict, List


def build_capa_items(findings: List[Dict[str, str]]) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    for idx, finding in enumerate(findings, start=1):
        risk = finding.get("风险等级", "中")
        module = finding.get("问题分类", "")
        if risk == "高":
            due = "7个工作日内完成初步纠正，15个工作日内完成CAPA计划"
            priority = "高"
        elif risk == "中":
            due = "15个工作日内完成纠正和原因分析"
            priority = "中"
        else:
            due = "30个工作日内完成记录和趋势观察"
            priority = "低"
        items.append(
            {
                "序号": str(idx),
                "问题分类": module,
                "问题描述": finding.get("问题描述", ""),
                "风险等级": risk,
                "优先级": priority,
                "根因分析方向": suggest_root_cause(module),
                "纠正措施": suggest_correction(module),
                "预防措施": suggest_prevention(module),
                "责任部门/人员": "项目组/中心研究团队/申办方质控负责人待确认",
                "完成期限": due,
                "验证方式": "复核补充证据、同类样本横向排查、CAPA关闭证据确认",
                "状态": "待制定",
            }
        )
    return items


def suggest_root_cause(module: str) -> str:
    mapping = {
        "知情同意": "版本控制、授权培训、筛选前流程控制、研究者执行意识不足",
        "入排标准": "入排判断流程不清、关键检查结果获取与审核时序控制不足",
        "访视与方案依从性": "访视预约管理、窗口期提醒、偏离识别与记录机制不足",
        "EDC与源文件一致性": "源数据录入、Query处理、研究者审核、数据核对流程不足",
        "稽查前准备": "项目资料管理、稽查前清单确认和资料交接机制不足",
    }
    return mapping.get(module, "流程执行、培训、复核和记录管理不足")


def suggest_correction(module: str) -> str:
    mapping = {
        "知情同意": "补充核对ICF版本、签署页、伦理批件、授权表和培训记录，必要时开展同类受试者排查。",
        "入排标准": "补充入排判断依据，确认研究者在入组前是否已掌握关键结果，并复核同类受试者。",
        "访视与方案依从性": "补充访视偏离说明，核对关键检查是否完成，必要时补录偏离并评估影响。",
        "EDC与源文件一致性": "更正EDC或补充Query解释，保留源文件、Query和审核证据。",
        "稽查前准备": "补齐缺失资料，明确本次稽查受限范围和后续补充时间。",
    }
    return mapping.get(module, "补充事实证据，明确影响范围，完成问题确认和纠正。")


def suggest_prevention(module: str) -> str:
    mapping = {
        "知情同意": "建立ICF版本、授权和培训的操作前核对机制。",
        "入排标准": "建立入组前关键依据清单和研究者复核签认机制。",
        "访视与方案依从性": "建立访视窗口自动提醒和偏离及时记录机制。",
        "EDC与源文件一致性": "建立关键字段SDV/SDR和Query根因追踪机制。",
        "稽查前准备": "建立稽查前资料清单和缺失资料升级机制。",
    }
    return mapping.get(module, "完善SOP培训、复核清单和质量趋势分析机制。")
