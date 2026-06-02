from datetime import datetime
import streamlit as st

from src.guide_engine import (
    DEFAULT_WORKFLOW,
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

st.set_page_config(page_title="AI引导式稽查SOP执行系统", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.2rem;}
.step-card {border: 1px solid #d9e2ef; border-radius: 12px; padding: 16px; background: #f8fbff; margin-bottom: 12px;}
.risk-high {color:#b00020; font-weight:700;}
.risk-medium {color:#b36b00; font-weight:700;}
.risk-low {color:#276749; font-weight:700;}
</style>
""", unsafe_allow_html=True)

init_session()

st.title("AI引导式稽查SOP执行系统")
st.caption("流程驱动 + 规则判断 + 证据链记录 + 报告初稿生成。")

with st.sidebar:
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

    st.divider()
    st.header("流程进度")
    for i, step_item in enumerate(DEFAULT_WORKFLOW):
        icon = "已完成" if i in st.session_state.done_steps else ("当前" if i == st.session_state.current_index else "待执行")
        if st.button(f"{icon}｜{i+1}. {step_item['module']}", key=f"nav_{i}", use_container_width=True):
            st.session_state.current_index = i
            st.rerun()

step = get_current_step()
left, mid, right = st.columns([1.15, 1.7, 1.15], gap="large")

with left:
    st.subheader("当前任务卡")
    st.markdown(f"""
<div class='step-card'>
<b>模块：</b>{step['module']}<br>
<b>步骤：</b>{step['step_name']}<br>
<b>现在做什么：</b>{step['instruction']}<br>
</div>
""", unsafe_allow_html=True)

    st.markdown("**需要查看的资料**")
    for item in step["documents"]:
        st.checkbox(item, key=f"doc_{step['id']}_{item}")

    st.markdown("**常见风险提醒**")
    for risk in step["common_risks"]:
        st.write(f"- {risk}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("已查看", use_container_width=True):
            mark_step_done()
            st.success("已标记完成")
        if st.button("返回上一步", use_container_width=True):
            previous_step()
            st.rerun()
    with c2:
        if st.button("发现异常", use_container_width=True):
            st.session_state.last_result = evaluate_current_step()
        if st.button("进入下一步", use_container_width=True):
            mark_step_done()
            next_step()
            st.rerun()

with mid:
    st.subheader("AI逐步引导")
    st.info(step["ai_prompt"])

    st.markdown("**请按提示填写或粘贴证据信息**")
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

    uploaded = st.file_uploader("可上传照片/截图/文件作为证据（当前版本保存文件名）", accept_multiple_files=True)
    if uploaded:
        st.session_state.evidence_files[step["id"]] = [f.name for f in uploaded]
        st.success("已记录证据文件名：" + "；".join(st.session_state.evidence_files[step["id"]]))

    if st.button("AI判断当前步骤", type="primary"):
        st.session_state.last_result = evaluate_current_step()

    result = st.session_state.get("last_result")
    if result and result.get("step_id") == step["id"]:
        risk_class = {"高": "risk-high", "中": "risk-medium", "低": "risk-low"}.get(result["risk_level"], "risk-low")
        st.markdown(f"**判断结果：** <span class='{risk_class}'>{result['risk_level']}风险</span>", unsafe_allow_html=True)
        st.write(result["summary"])
        if result["questions"]:
            st.markdown("**AI建议继续追问/补充证据：**")
            for question in result["questions"]:
                st.write(f"- {question}")
        if result["triggered_rules"]:
            with st.expander("查看触发规则"):
                for rule in result["triggered_rules"]:
                    st.write(f"- {rule}")
        if st.button("根据判断生成标准记录"):
            st.session_state.records.append(build_finding_from_current_step(result))
            st.success("已加入发现记录区。")

with right:
    st.subheader("发现记录区")
    if not st.session_state.records:
        st.caption("当前暂无记录。")
    else:
        for idx, rec in enumerate(st.session_state.records, start=1):
            with st.expander(f"{idx}. {rec['问题分类']}｜{rec['风险等级']}｜{rec['问题标题']}", expanded=idx == len(st.session_state.records)):
                for key in ["问题描述", "证据来源", "风险影响", "建议措施", "状态"]:
                    st.write(f"**{key}：**", rec.get(key, ""))

    st.divider()
    st.subheader("导出")
    df = export_records_dataframe()
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("下载问题清单CSV", data=csv, file_name="AI引导稽查问题清单.csv", mime="text/csv", use_container_width=True)
    st.download_button("下载Word报告初稿", data=build_word_report(), file_name="AI引导式稽查报告初稿.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

st.divider()
with st.expander("开发说明 / 后续扩展"):
    st.write("当前版本为可运行MVP：包含流程导航、任务卡、字段采集、规则判断、补充追问、证据链记录、问题清单和Word报告导出。后续可接入OCR、知识库、大模型、EDC自动解析、权限和数据库。")
