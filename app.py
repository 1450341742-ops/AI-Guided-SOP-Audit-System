from datetime import datetime
import pandas as pd
import streamlit as st

from src.auth import has_permission, login_box, logout_button
from src.capa import build_capa_items
from src.config_manager import load_workflow_config, reset_workflow_config, save_workflow_config, text_to_workflow, workflow_to_text
from src.exporters import build_excel_package
from src.file_parsers import parse_uploaded_file
from src.guide_engine import (
    init_session,
    get_current_step,
    evaluate_current_step,
    next_step,
    previous_step,
    mark_step_done,
    build_finding_from_current_step,
    export_records_dataframe,
    build_word_report,
)
from src.knowledge_base import build_guidance_text
from src.storage import (
    create_project,
    get_project,
    init_db,
    list_projects,
    load_findings,
    load_logs,
    load_step_inputs,
    load_uploaded_files,
    save_finding,
    save_step_input,
    save_uploaded_file_summary,
    update_finding_review,
    update_project,
)
from src.ui_style import apply_tech_style, hero

st.set_page_config(page_title="AI引导式稽查SOP执行系统", layout="wide")

if not login_box():
    st.stop()

init_db()
init_session()
apply_tech_style()
logout_button()

WORKFLOW = load_workflow_config()

hero(
    "AI引导式稽查SOP执行系统 V3",
    "蓝白科技风界面｜现场流程导航、证据链判断、发现复核、CAPA生成与交付整包导出一体化。",
    "Clinical Trial Quality Intelligence",
)

st.session_state.setdefault("project_id", None)
st.session_state.setdefault("selected_page", "现场引导")

with st.sidebar:
    st.header("项目管理")
    projects = list_projects()
    project_options = {f"{p['id']}｜{p['project_name']}｜{p.get('site_no','')}": p["id"] for p in projects}
    selected = st.selectbox("打开历史项目", ["新建项目"] + list(project_options.keys()))
    if selected != "新建项目" and st.button("加载项目", use_container_width=True):
        pid = project_options[selected]
        p = get_project(pid)
        if p:
            st.session_state.project_id = pid
            st.session_state.project = p
            st.session_state.step_inputs = load_step_inputs(pid)
            st.session_state.records = load_findings(pid)
            st.success("项目已加载")
            st.rerun()

    st.divider()
    st.header("项目设置")
    st.session_state.project.update({
        "project_name": st.text_input("项目名称", st.session_state.project.get("project_name", "")),
        "sponsor": st.text_input("申办方", st.session_state.project.get("sponsor", "")),
        "site_no": st.text_input("中心编号", st.session_state.project.get("site_no", "")),
        "auditor": st.text_input("稽查员", st.session_state.project.get("auditor", "")),
        "audit_type": st.selectbox("稽查类型", ["现场稽查", "远程质控", "模拟核查", "专项稽查"], index=0),
        "subject_id": st.text_input("当前受试者编号", st.session_state.project.get("subject_id", "")),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    cnew, csave = st.columns(2)
    with cnew:
        if st.button("新建保存", use_container_width=True, disabled=not has_permission("create")):
            st.session_state.project_id = create_project(st.session_state.project)
            st.success(f"已创建项目ID：{st.session_state.project_id}")
    with csave:
        if st.button("保存项目", use_container_width=True, disabled=not has_permission("save")):
            if st.session_state.project_id:
                update_project(st.session_state.project_id, st.session_state.project)
                st.success("已保存")
            else:
                st.warning("请先点击新建保存")

    st.divider()
    st.header("页面")
    pages = ["现场引导", "发现复核", "CAPA计划", "文件解析", "项目日志"]
    if has_permission("config"):
        pages.append("后台配置")
    st.session_state.selected_page = st.radio("选择功能", pages, label_visibility="collapsed")

    st.divider()
    st.header("流程进度")
    from src.guide_engine import DEFAULT_WORKFLOW
    for i, step_item in enumerate(DEFAULT_WORKFLOW):
        icon = "已完成" if i in st.session_state.done_steps else ("当前" if i == st.session_state.current_index else "待执行")
        if st.button(f"{icon}｜{i+1}. {step_item['module']}", key=f"nav_{i}", use_container_width=True):
            st.session_state.current_index = i
            st.rerun()

if st.session_state.selected_page == "后台配置":
    st.subheader("后台流程配置")
    if not has_permission("config"):
        st.error("当前账号无后台配置权限。")
        st.stop()
    st.caption("当前配置页用于调整流程提示文案和字段。若JSON填写错误，可重置为默认配置。")
    config_text = st.text_area("流程JSON配置", value=workflow_to_text(WORKFLOW), height=520)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("保存配置", type="primary"):
            try:
                workflow = text_to_workflow(config_text)
                save_workflow_config(workflow)
                st.success("配置已保存，刷新后生效。")
            except Exception as exc:
                st.error(f"配置保存失败：{exc}")
    with col_b:
        if st.button("恢复默认配置"):
            reset_workflow_config()
            st.success("已恢复默认配置。")
    st.stop()

if st.session_state.selected_page == "文件解析":
    st.subheader("文件解析与资料预审")
    if not st.session_state.project_id:
        st.info("请先新建或加载项目。")
        st.stop()
    files = st.file_uploader("上传xlsx、csv、docx、txt文件", accept_multiple_files=True, type=["xlsx", "xls", "csv", "docx", "txt"])
    if files:
        for f in files:
            parsed = parse_uploaded_file(f.name, f.getvalue())
            save_uploaded_file_summary(st.session_state.project_id, f.name, parsed.get("type", ""), parsed.get("summary", ""))
            with st.expander(f"{f.name}｜{parsed.get('type', '')}", expanded=True):
                st.text(parsed.get("summary", ""))
        st.success("文件解析摘要已保存。")
    st.markdown("**历史解析记录**")
    st.dataframe(pd.DataFrame(load_uploaded_files(st.session_state.project_id)), use_container_width=True)
    st.stop()

if st.session_state.selected_page == "发现复核":
    st.subheader("发现复核")
    if not st.session_state.project_id:
        st.info("请先加载或新建项目。")
        st.stop()
    records = load_findings(st.session_state.project_id)
    if not records:
        st.info("暂无发现记录。")
        st.stop()
    for rec in records:
        with st.expander(f"ID {rec.get('记录ID')}｜{rec.get('问题分类')}｜{rec.get('风险等级')}｜{rec.get('复核状态')}"):
            st.write(rec.get("问题描述", ""))
            st.write("证据来源：", rec.get("证据来源", ""))
            st.write("建议措施：", rec.get("建议措施", ""))
            status = st.selectbox("复核状态", ["待复核", "通过", "退回修改", "需升级确认"], index=["待复核", "通过", "退回修改", "需升级确认"].index(rec.get("复核状态", "待复核")) if rec.get("复核状态") in ["待复核", "通过", "退回修改", "需升级确认"] else 0, key=f"review_status_{rec.get('记录ID')}")
            comment = st.text_area("复核意见", value=rec.get("复核意见", ""), key=f"review_comment_{rec.get('记录ID')}")
            if st.button("保存复核", key=f"save_review_{rec.get('记录ID')}", disabled=not has_permission("review")):
                update_finding_review(st.session_state.project_id, int(rec.get("记录ID")), status, comment, st.session_state.user.display_name)
                st.success("复核已保存")
                st.rerun()
    st.stop()

if st.session_state.selected_page == "CAPA计划":
    st.subheader("CAPA自动生成")
    if not st.session_state.records:
        st.info("暂无发现记录。请先在现场引导页面生成问题记录。")
    else:
        capa_items = build_capa_items(st.session_state.records)
        capa_df = pd.DataFrame(capa_items)
        st.dataframe(capa_df, use_container_width=True)
        st.download_button("下载CAPA计划CSV", data=capa_df.to_csv(index=False).encode("utf-8-sig"), file_name="AI生成CAPA计划.csv", mime="text/csv")
    st.stop()

if st.session_state.selected_page == "项目日志":
    st.subheader("项目操作日志")
    if st.session_state.project_id:
        logs = load_logs(st.session_state.project_id)
        st.dataframe(pd.DataFrame(logs), use_container_width=True)
    else:
        st.info("请先加载或新建项目。")
    st.stop()

step = get_current_step()
if st.session_state.project_id:
    st.session_state.records = load_findings(st.session_state.project_id)

records_count = len(st.session_state.records)
done_count = len(st.session_state.done_steps)
high_count = sum(1 for r in st.session_state.records if r.get("风险等级") == "高")
medium_count = sum(1 for r in st.session_state.records if r.get("风险等级") == "中")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("当前项目", st.session_state.project_id or "未保存")
col_m2.metric("流程完成", f"{done_count}/{len(DEFAULT_WORKFLOW)}")
col_m3.metric("发现记录", records_count)
col_m4.metric("中高风险", high_count + medium_count)

st.markdown("<br>", unsafe_allow_html=True)
main_tab, finding_tab = st.tabs(["当前步骤执行", "发现记录与导出"])

with main_tab:
    task_col, work_col = st.columns([0.95, 1.65], gap="large")

    with task_col:
        st.markdown(f"""
<div class='step-card'>
<div class='step-chip'>Current Step</div>
<div class='step-title'>{step['module']}</div>
<b>步骤：</b>{step['step_name']}<br><br>
<b>现在做什么：</b><br>{step['instruction']}
</div>
""", unsafe_allow_html=True)

        with st.expander("需要查看的资料", expanded=True):
            for item in step["documents"]:
                st.checkbox(item, key=f"doc_{step['id']}_{item}")

        with st.expander("常见风险提醒", expanded=False):
            for risk in step["common_risks"]:
                st.write(f"- {risk}")

        st.markdown("**流程操作**")
        a1, a2 = st.columns(2)
        with a1:
            if st.button("已查看", use_container_width=True):
                mark_step_done()
                st.success("已标记完成")
            if st.button("返回上一步", use_container_width=True):
                previous_step()
                st.rerun()
        with a2:
            if st.button("发现异常", use_container_width=True):
                st.session_state.last_result = evaluate_current_step()
            if st.button("进入下一步", use_container_width=True):
                mark_step_done()
                next_step()
                st.rerun()

    with work_col:
        st.markdown("<div class='panel-card'><div class='step-title'>AI逐步引导</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-strip'>{step['ai_prompt']}</div>", unsafe_allow_html=True)

        with st.expander("知识库提示", expanded=True):
            current_text = " ".join(str(v) for v in st.session_state.step_inputs.get(step["id"], {}).values())
            st.markdown(f"<div class='kb-box'>{build_guidance_text(step['module'], current_text)}</div>", unsafe_allow_html=True)

        st.markdown("**证据信息填写**")
        st.session_state.step_inputs.setdefault(step["id"], {})
        for field in step["fields"]:
            current_value = st.session_state.step_inputs[step["id"]].get(field["key"], "")
            widget_key = f"field_{step['id']}_{field['key']}"
            if field.get("type") == "date":
                value = st.text_input(field["label"], value=current_value, placeholder="YYYY-MM-DD", key=widget_key)
            elif field.get("type") == "textarea":
                value = st.text_area(field["label"], value=current_value, height=90, key=widget_key)
            else:
                value = st.text_input(field["label"], value=current_value, key=widget_key)
            st.session_state.step_inputs[step["id"]][field["key"]] = value

        st.markdown("<br>", unsafe_allow_html=True)
        op1, op2, op3 = st.columns([1, 1, 1])
        with op1:
            if st.button("保存当前步骤", disabled=not has_permission("save"), use_container_width=True):
                if st.session_state.project_id:
                    save_step_input(st.session_state.project_id, step["id"], st.session_state.step_inputs[step["id"]])
                    st.success("当前步骤已保存到数据库")
                else:
                    st.warning("请先新建保存项目")
        with op2:
            if st.button("AI判断", type="primary", use_container_width=True):
                st.session_state.last_result = evaluate_current_step()
        with op3:
            uploaded = st.file_uploader("上传证据", accept_multiple_files=True, label_visibility="collapsed")
            if uploaded:
                st.session_state.evidence_files[step["id"]] = [f.name for f in uploaded]
                st.success("已记录证据文件名")

        result = st.session_state.get("last_result")
        if result and result.get("step_id") == step["id"]:
            st.divider()
            risk_class = {"高": "risk-high", "中": "risk-medium", "低": "risk-low"}.get(result["risk_level"], "risk-low")
            st.markdown(f"**判断结果：** <span class='{risk_class}'>{result['risk_level']}风险</span>", unsafe_allow_html=True)
            st.write(result["summary"])
            if result["questions"]:
                with st.expander("AI建议继续追问/补充证据", expanded=True):
                    for question in result["questions"]:
                        st.write(f"- {question}")
            if result["triggered_rules"]:
                with st.expander("查看触发规则", expanded=False):
                    for rule in result["triggered_rules"]:
                        st.write(f"- {rule}")
            if st.button("根据判断生成标准记录", disabled=not has_permission("save"), use_container_width=True):
                finding = build_finding_from_current_step(result)
                st.session_state.records.append(finding)
                if st.session_state.project_id:
                    save_finding(st.session_state.project_id, finding)
                st.success("已加入发现记录区。")
        st.markdown("</div>", unsafe_allow_html=True)

with finding_tab:
    list_col, export_col = st.columns([1.55, 0.95], gap="large")
    with list_col:
        st.markdown("<div class='panel-card'><div class='step-title'>发现记录区</div>", unsafe_allow_html=True)
        if not st.session_state.records:
            st.caption("当前暂无记录。")
        else:
            for idx, rec in enumerate(st.session_state.records, start=1):
                with st.expander(f"{idx}. {rec.get('问题分类')}｜{rec.get('风险等级')}｜{rec.get('复核状态', '待复核')}｜{rec.get('问题标题')}"):
                    for key in ["问题描述", "证据来源", "风险影响", "建议措施", "复核意见", "状态"]:
                        st.write(f"**{key}：**", rec.get(key, ""))
        st.markdown("</div>", unsafe_allow_html=True)

    with export_col:
        st.markdown("<div class='panel-card'><div class='step-title'>导出交付</div>", unsafe_allow_html=True)
        st.caption("将问题、报告、CAPA和日志拆分导出，便于项目归档。")
        df = export_records_dataframe()
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("下载问题清单CSV", data=csv, file_name="AI引导稽查问题清单.csv", mime="text/csv", use_container_width=True, disabled=not has_permission("export"))
        st.download_button("下载Word报告初稿", data=build_word_report(), file_name="AI引导式稽查报告初稿.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True, disabled=not has_permission("export"))
        logs_for_export = load_logs(st.session_state.project_id) if st.session_state.project_id else []
        st.download_button("下载Excel整包", data=build_excel_package(st.session_state.records, logs_for_export), file_name="AI引导稽查交付整包.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, disabled=not has_permission("export"))
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='footer-note'>提升质量，赋能上市｜AI Guided Audit SOP System</div>", unsafe_allow_html=True)
