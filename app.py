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
    load_knowledge_files,
    load_logs,
    load_step_inputs,
    load_uploaded_files,
    list_knowledge_categories,
    save_finding,
    save_knowledge_file,
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
st.session_state.setdefault("project_id", None)
st.session_state.setdefault("module_page", "工作台首页")

hero(
    "AI引导式稽查SOP执行系统 V4",
    "项目库、知识库、现场引导、发现复核、CAPA与交付整包分层管理，让稽查员按标准流程完成每一步。",
    "Quality Intelligence Platform",
)

with st.sidebar:
    st.header("系统导航")
    pages = ["工作台首页", "项目库", "知识库", "稽查执行", "发现复核", "交付中心"]
    if has_permission("config"):
        pages.append("后台配置")
    st.session_state.module_page = st.radio("页面", pages, label_visibility="collapsed")

    st.divider()
    st.header("当前项目")
    projects = list_projects(80)
    project_options = {f"{p['id']}｜{p['project_name']}｜{p.get('site_no','')}": p["id"] for p in projects}
    selected = st.selectbox("选择项目", ["未选择"] + list(project_options.keys()))
    if selected != "未选择" and st.button("加载项目", use_container_width=True):
        pid = project_options[selected]
        p = get_project(pid)
        if p:
            st.session_state.project_id = pid
            st.session_state.project = p
            st.session_state.step_inputs = load_step_inputs(pid)
            st.session_state.records = load_findings(pid)
            st.success("项目已加载")
            st.rerun()

    if st.session_state.project_id:
        st.caption(f"已加载项目ID：{st.session_state.project_id}")
        st.caption(st.session_state.project.get("project_name", ""))
    else:
        st.caption("尚未加载项目")

from src.guide_engine import DEFAULT_WORKFLOW


def refresh_records() -> None:
    if st.session_state.project_id:
        st.session_state.records = load_findings(st.session_state.project_id)


def project_form(prefix: str = "") -> dict:
    col1, col2, col3 = st.columns(3)
    with col1:
        project_name = st.text_input("项目名称", st.session_state.project.get("project_name", ""), key=f"{prefix}project_name")
        sponsor = st.text_input("申办方", st.session_state.project.get("sponsor", ""), key=f"{prefix}sponsor")
    with col2:
        site_no = st.text_input("中心编号", st.session_state.project.get("site_no", ""), key=f"{prefix}site_no")
        subject_id = st.text_input("当前受试者编号", st.session_state.project.get("subject_id", ""), key=f"{prefix}subject_id")
    with col3:
        auditor = st.text_input("稽查员", st.session_state.project.get("auditor", ""), key=f"{prefix}auditor")
        audit_type = st.selectbox("稽查类型", ["现场稽查", "远程质控", "模拟核查", "专项稽查"], index=0, key=f"{prefix}audit_type")
    return {
        "project_name": project_name,
        "sponsor": sponsor,
        "site_no": site_no,
        "auditor": auditor,
        "audit_type": audit_type,
        "subject_id": subject_id,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


if st.session_state.module_page == "工作台首页":
    refresh_records()
    projects = list_projects(100)
    kb_files = load_knowledge_files()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("项目库项目", len(projects))
    c2.metric("当前项目ID", st.session_state.project_id or "未选择")
    c3.metric("当前发现", len(st.session_state.records))
    c4.metric("知识库文件", len(kb_files))

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        st.markdown("<div class='panel-card'><div class='step-title'>系统架构</div>", unsafe_allow_html=True)
        st.write("第一层：项目库，统一管理项目、中心、受试者和稽查过程数据。")
        st.write("第二层：知识库，沉淀法规、SOP、模板、历史稽查记录、方案和项目资料。")
        st.write("第三层：稽查执行，按流程引导稽查员逐步查看、判断、记录。")
        st.write("第四层：发现复核与交付，完成复核、CAPA、报告和整包导出。")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='panel-card'><div class='step-title'>建议操作路径</div>", unsafe_allow_html=True)
        st.write("1. 先进入项目库，新建或加载项目。")
        st.write("2. 进入知识库，上传法规、SOP、方案、EDC、历史问题等资料。")
        st.write("3. 进入稽查执行，按当前步骤完成现场动作。")
        st.write("4. 进入发现复核，确认问题质量。")
        st.write("5. 进入交付中心，导出问题清单、报告、CAPA和整包。")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


if st.session_state.module_page == "项目库":
    st.subheader("项目库")
    tab_new, tab_list, tab_files = st.tabs(["新建/编辑项目", "项目列表", "项目资料库"])

    with tab_new:
        st.markdown("<div class='panel-card'><div class='step-title'>项目基础信息</div>", unsafe_allow_html=True)
        data = project_form("project_")
        a, b = st.columns([1, 1])
        with a:
            if st.button("新建项目", use_container_width=True, disabled=not has_permission("create")):
                st.session_state.project_id = create_project(data)
                st.session_state.project = data
                st.success(f"已创建项目ID：{st.session_state.project_id}")
        with b:
            if st.button("保存当前项目", use_container_width=True, disabled=not has_permission("save")):
                if st.session_state.project_id:
                    update_project(st.session_state.project_id, data)
                    st.session_state.project = data
                    st.success("已保存当前项目")
                else:
                    st.warning("请先新建或加载项目")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_list:
        st.markdown("<div class='panel-card'><div class='step-title'>项目列表</div>", unsafe_allow_html=True)
        df = pd.DataFrame(list_projects(200))
        st.dataframe(df, use_container_width=True, height=420)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_files:
        st.markdown("<div class='panel-card'><div class='step-title'>项目资料库</div>", unsafe_allow_html=True)
        if not st.session_state.project_id:
            st.info("请先加载或新建项目。")
        else:
            files = st.file_uploader("上传项目资料：图片、Word、PDF、Excel、PPT、TXT", accept_multiple_files=True, type=["png", "jpg", "jpeg", "webp", "bmp", "docx", "pdf", "xlsx", "xls", "csv", "pptx", "txt"], key="project_file_uploader")
            if files:
                for f in files:
                    parsed = parse_uploaded_file(f.name, f.getvalue())
                    save_uploaded_file_summary(st.session_state.project_id, f.name, parsed.get("type", ""), parsed.get("summary", ""))
                st.success("项目资料已解析并保存。")
            st.dataframe(pd.DataFrame(load_uploaded_files(st.session_state.project_id)), use_container_width=True, height=360)
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


if st.session_state.module_page == "知识库":
    st.subheader("知识库")
    kb_upload, kb_search = st.tabs(["上传知识库", "检索知识库"])

    with kb_upload:
        st.markdown("<div class='panel-card'><div class='step-title'>上传知识库文件</div>", unsafe_allow_html=True)
        k1, k2, k3 = st.columns([1, 1, 1])
        with k1:
            kb_name = st.text_input("知识库名称", value="公司稽查知识库")
        with k2:
            category = st.selectbox("资料分类", ["法规指南", "公司SOP", "稽查模板", "历史稽查记录", "项目方案", "EDC资料", "培训资料", "商务案例", "其他"])
        with k3:
            tags = st.text_input("标签", placeholder="如：ICF、AE、EDC、CFDI")
        kb_files = st.file_uploader("支持图片、Word、PDF、Excel、PPT、TXT", accept_multiple_files=True, type=["png", "jpg", "jpeg", "webp", "bmp", "docx", "pdf", "xlsx", "xls", "csv", "pptx", "txt"], key="kb_file_uploader")
        if kb_files and st.button("解析并保存到知识库", type="primary", disabled=not has_permission("save")):
            for f in kb_files:
                parsed = parse_uploaded_file(f.name, f.getvalue())
                save_knowledge_file(kb_name, category, f.name, parsed.get("type", ""), parsed.get("summary", ""), tags)
            st.success("已保存到知识库。")
        st.markdown("</div>", unsafe_allow_html=True)

    with kb_search:
        st.markdown("<div class='panel-card'><div class='step-title'>检索知识库</div>", unsafe_allow_html=True)
        s1, s2 = st.columns([1.4, 0.8])
        with s1:
            keyword = st.text_input("关键词检索", placeholder="输入 ICF、AE、EDC、方案、授权、培训等")
        with s2:
            categories = ["全部"] + list_knowledge_categories()
            selected_category = st.selectbox("分类", categories)
        rows = load_knowledge_files(keyword, selected_category)
        st.caption(f"检索结果：{len(rows)} 条")
        if rows:
            for row in rows[:30]:
                with st.expander(f"{row['category']}｜{row['file_name']}｜{row['file_type']}"):
                    st.write("知识库：", row.get("kb_name", ""))
                    st.write("标签：", row.get("tags", ""))
                    st.text(row.get("summary", "")[:5000])
        else:
            st.info("暂无匹配知识。")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


if st.session_state.module_page == "后台配置":
    st.subheader("后台流程配置")
    if not has_permission("config"):
        st.error("当前账号无后台配置权限。")
        st.stop()
    st.caption("用于调整流程提示文案和字段。若JSON填写错误，可重置为默认配置。")
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


if st.session_state.module_page == "发现复核":
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
            status = st.selectbox("复核状态", ["待复核", "通过", "退回修改", "需升级确认"], key=f"review_status_{rec.get('记录ID')}")
            comment = st.text_area("复核意见", value=rec.get("复核意见", ""), key=f"review_comment_{rec.get('记录ID')}")
            if st.button("保存复核", key=f"save_review_{rec.get('记录ID')}", disabled=not has_permission("review")):
                update_finding_review(st.session_state.project_id, int(rec.get("记录ID")), status, comment, st.session_state.user.display_name)
                st.success("复核已保存")
                st.rerun()
    st.stop()


if st.session_state.module_page == "交付中心":
    st.subheader("交付中心")
    refresh_records()
    if not st.session_state.project_id:
        st.info("请先加载或新建项目。")
        st.stop()
    t1, t2, t3 = st.tabs(["问题清单", "CAPA计划", "导出整包"])
    with t1:
        st.dataframe(pd.DataFrame(st.session_state.records), use_container_width=True, height=420)
    with t2:
        capa_df = pd.DataFrame(build_capa_items(st.session_state.records)) if st.session_state.records else pd.DataFrame()
        st.dataframe(capa_df, use_container_width=True, height=420)
    with t3:
        st.markdown("<div class='panel-card'><div class='step-title'>交付文件导出</div>", unsafe_allow_html=True)
        df = export_records_dataframe()
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("下载问题清单CSV", data=csv, file_name="AI引导稽查问题清单.csv", mime="text/csv", use_container_width=True, disabled=not has_permission("export"))
        st.download_button("下载Word报告初稿", data=build_word_report(), file_name="AI引导式稽查报告初稿.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True, disabled=not has_permission("export"))
        logs_for_export = load_logs(st.session_state.project_id)
        st.download_button("下载Excel整包", data=build_excel_package(st.session_state.records, logs_for_export), file_name="AI引导稽查交付整包.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, disabled=not has_permission("export"))
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# 稽查执行页面
if st.session_state.module_page == "稽查执行":
    st.subheader("稽查执行")
    if not st.session_state.project_id:
        st.info("请先在项目库中新建或加载项目。")
        st.stop()
    refresh_records()
    step = get_current_step()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("当前项目", st.session_state.project_id)
    c2.metric("流程完成", f"{len(st.session_state.done_steps)}/{len(DEFAULT_WORKFLOW)}")
    c3.metric("发现记录", len(st.session_state.records))
    c4.metric("高风险", sum(1 for r in st.session_state.records if r.get("风险等级") == "高"))

    st.markdown("<br>", unsafe_allow_html=True)
    main_tab, records_tab = st.tabs(["当前步骤", "本项目发现"])
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
            with st.expander("流程导航", expanded=True):
                for i, step_item in enumerate(DEFAULT_WORKFLOW):
                    icon = "已完成" if i in st.session_state.done_steps else ("当前" if i == st.session_state.current_index else "待执行")
                    if st.button(f"{icon}｜{i+1}. {step_item['module']}", key=f"exec_nav_{i}", use_container_width=True):
                        st.session_state.current_index = i
                        st.rerun()
            with st.expander("需要查看资料", expanded=True):
                for item in step["documents"]:
                    st.checkbox(item, key=f"doc_{step['id']}_{item}")
            with st.expander("常见风险提醒", expanded=False):
                for risk in step["common_risks"]:
                    st.write(f"- {risk}")
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
            op1, op2, op3 = st.columns([1, 1, 1])
            with op1:
                if st.button("保存当前步骤", disabled=not has_permission("save"), use_container_width=True):
                    save_step_input(st.session_state.project_id, step["id"], st.session_state.step_inputs[step["id"]])
                    st.success("当前步骤已保存")
            with op2:
                if st.button("AI判断", type="primary", use_container_width=True):
                    st.session_state.last_result = evaluate_current_step()
            with op3:
                uploaded = st.file_uploader("上传证据", accept_multiple_files=True, label_visibility="collapsed", key="execution_evidence")
                if uploaded:
                    st.session_state.evidence_files[step["id"]] = [f.name for f in uploaded]
                    st.success("已记录证据")
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
                if st.button("根据判断生成标准记录", disabled=not has_permission("save"), use_container_width=True):
                    finding = build_finding_from_current_step(result)
                    st.session_state.records.append(finding)
                    save_finding(st.session_state.project_id, finding)
                    st.success("已加入发现记录区。")
            st.markdown("</div>", unsafe_allow_html=True)

    with records_tab:
        st.markdown("<div class='panel-card'><div class='step-title'>本项目发现记录</div>", unsafe_allow_html=True)
        if not st.session_state.records:
            st.caption("当前暂无记录。")
        else:
            for idx, rec in enumerate(st.session_state.records, start=1):
                with st.expander(f"{idx}. {rec.get('问题分类')}｜{rec.get('风险等级')}｜{rec.get('复核状态', '待复核')}｜{rec.get('问题标题')}"):
                    for key in ["问题描述", "证据来源", "风险影响", "建议措施", "复核意见", "状态"]:
                        st.write(f"**{key}：**", rec.get(key, ""))
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='footer-note'>提升质量，赋能上市｜AI Guided Audit SOP System</div>", unsafe_allow_html=True)
