import uuid
import streamlit as st

from orchestrator import orchestrate, confirm_appointment
from ui_texts import make_translator, display_drug_name
from ui_styles import inject_css
from ui_helpers import format_local_time
from ui_components import (
    render_sidebar,
    render_progress,
    render_result_turn,
)

st.set_page_config(
    page_title="Medical Agent",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

if "lang" not in st.session_state:
    st.session_state["lang"] = "zh-Hans"
if "session_id" not in st.session_state:
    st.session_state.session_id = f"sess_{uuid.uuid4().hex[:8]}"
if "history" not in st.session_state:
    st.session_state.history = []
if "patient_name" not in st.session_state:
    st.session_state["patient_name"] = ""
if "greeted_name" not in st.session_state:
    st.session_state.greeted_name = None

t = make_translator(st)

# 侧边栏
render_sidebar(t)

# 主标题（白大褂医生 SVG）
st.markdown(
    f'<div class="hero-title" style="display:flex;align-items:center;gap:0.7rem;">'
    f'<svg width="44" height="44" viewBox="0 0 24 24" fill="none" '
    f'stroke="#4f46e5" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    f'<circle cx="12" cy="6.5" r="3.5"/>'
    f'<path d="M4.5 20.5v-2a5 5 0 0 1 5-5h5a5 5 0 0 1 5 5v2"/>'
    f'<path d="M12 13.5v7"/>'
    f'<path d="M8.5 15c0 1.5 1.5 3 3.5 3s3.5-1.5 3.5-3"/>'
    f'</svg>'
    f'<span>{t("title")}</span>'
    f'</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="hero-subtitle">{t("subtitle")}</div>',
    unsafe_allow_html=True,
)

# 空状态
if not st.session_state.history:
    st.markdown(
        f'<div class="empty-state">'
        f'<div class="empty-title">{t("empty_title")}</div>'
        f'<div class="empty-desc">{t("empty_desc")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# 预约回调
def _confirm_appointment_cb(session_id, reason, date_str, time_str, lang):
    return confirm_appointment(
        session_id=session_id,
        reason=reason,
        date_str=date_str,
        time_str=time_str,
        lang=lang,
    )


# 显示历史对话
for i, turn in enumerate(st.session_state.history):
    with st.chat_message("user"):
        st.markdown(f"{', '.join(turn['input'])}")
    with st.chat_message("assistant"):
        render_result_turn(
            t, turn["result"], turn["input"], i + 1,
            on_confirm_appointment=_confirm_appointment_cb,
        )

# 对话总结（多轮之后）
if len(st.session_state.history) >= 2:
    all_symptoms = (
        st.session_state.history[-1]["result"]
        .get("state", {})
        .get("symptoms_history", [])
    )
    all_drugs = []
    for turn in st.session_state.history:
        for rec in turn["result"].get("recommendations", []):
            dn = rec.get("drug_name", "")
            if dn and dn not in all_drugs:
                all_drugs.append(dn)
    all_causes = []
    for turn in st.session_state.history:
        for c in turn["result"].get("possible_causes", []):
            cond = c.get("condition", "")
            if cond and cond not in all_causes:
                all_causes.append(cond)

    all_severities = []
    emergency_symptoms = []
    for turn in st.session_state.history:
        r = turn["result"]
        if r.get("action") == "emergency_escalation":
            all_severities.append("emergency")
            normalized = r.get("normalized", [])
            if normalized:
                emergency_symptoms.extend(normalized)
            else:
                matched = r.get("matched", [])
                if matched:
                    emergency_symptoms.extend(matched)
        else:
            all_severities.append(r.get("severity", "mild"))
    severity_rank = {"emergency": 2, "moderate": 1, "mild": 0, "non-emergency": 0}
    latest_severity = max(all_severities, key=lambda s: severity_rank.get(s, 0)) if all_severities else "-"

    latest = st.session_state.history[-1]["result"]
    latest_appt = latest.get("appointment", {}) or {}
    appt_time = ""
    if latest_appt.get("scheduled"):
        appt_time = format_local_time(latest_appt.get("slot_utc", ""), st.session_state["lang"])

    sev_color = "#b91c1c" if latest_severity == "emergency" else "#0d9488"
    drugs_str = " · ".join([display_drug_name(d, st.session_state["lang"]) for d in all_drugs]) or "-"
    causes_str = " · ".join(all_causes) or "-"
    severity_display = latest_severity
    if emergency_symptoms:
        unique_emerg = list(set(emergency_symptoms))
        severity_display = f'{latest_severity} ({t("contains_emergency")}: {" · ".join(unique_emerg)})'

    # ---- 对话总结卡片（grid 布局，标签/值严格分列）----
    sum_html = (
        '<div style="border-top:1px solid #e5e7eb;'
        'padding-top:1.2rem;margin-top:2rem;margin-bottom:1rem;">'
        f'<div style="display:flex;align-items:center;gap:0.5rem;'
        f'margin-bottom:1rem;font-weight:800;color:#0a0a0a;font-size:1rem;'
        f'letter-spacing:-0.2px;">'
        f'<span>📋</span><span>{t("conversation_summary")}</span></div>'
        '<div style="display:grid;grid-template-columns:170px 1fr;'
        'gap:0.6rem 1rem;font-size:0.9rem;">'

        f'<div style="color:#71717a;font-weight:600;">{t("summary_symptoms")}</div>'
        f'<div style="color:#18181b;">' + " · ".join(all_symptoms) + '</div>'

        f'<div style="color:#71717a;font-weight:600;">{t("summary_severity")}</div>'
        f'<div style="color:{sev_color};font-weight:600;">{severity_display}</div>'

        f'<div style="color:#71717a;font-weight:600;">{t("summary_causes")}</div>'
        f'<div style="color:#18181b;">{causes_str}</div>'

        f'<div style="color:#71717a;font-weight:600;">{t("summary_drugs")}</div>'
        f'<div style="color:#18181b;">{drugs_str}</div>'
    )
    if appt_time:
        sum_html += (
            f'<div style="color:#71717a;font-weight:600;">{t("summary_appointment")}</div>'
            f'<div style="color:#18181b;font-family:SF Mono,Menlo,monospace;">{appt_time}</div>'
        )
    sum_html += '</div></div>'
    st.markdown(sum_html, unsafe_allow_html=True)

# 追问提示（底部聊天框上方）
if st.session_state.history:
    last_result = st.session_state.history[-1]["result"]
    last_fqs = last_result.get("_followup_questions", [])
    if last_fqs:
        st.markdown(
            '<div style="margin-top:2rem;margin-bottom:1rem;'
            'border-top:1px solid #e2e8f0;"></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="font-size:0.75rem;color:#94a3b8;'
            f'font-weight:500;letter-spacing:0.4px;margin-bottom:0.4rem;">'
            f'{t("followup_prompt")}</div>',
            unsafe_allow_html=True,
        )
        list_html = '<ul style="list-style:none;padding:0;margin:0 0 1rem 0;">'
        for q in last_fqs:
            list_html += (
                f'<li style="font-size:0.9rem;color:#475569;'
                f'line-height:1.7;padding:0.1rem 0;">· {q}</li>'
            )
        list_html += '</ul>'
        st.markdown(list_html, unsafe_allow_html=True)

# 底部聊天输入框
user_input = st.chat_input(t("input_placeholder"))

if user_input and user_input.strip():
    raw = user_input.replace("，", ",")
    symptoms = [s.strip() for s in raw.split(",") if s.strip()]
    if not symptoms:
        st.warning(t("no_history"))
    else:
        with st.chat_message("user"):
            st.markdown(f"{user_input}")
        with st.chat_message("assistant"):
            progress_placeholder = st.empty()
            render_progress(t, None, progress_placeholder)

            def on_progress(stage: str):
                render_progress(t, stage, progress_placeholder)

            hint_placeholder = st.empty()
            hint_placeholder.info("⏱️ " + t("analyzing_hint"))

            with st.status(t("analyzing"), expanded=False) as status:
                try:
                    result = orchestrate(
                        st.session_state.session_id,
                        symptoms,
                        st.session_state.get("patient_name") or None,
                        progress_callback=on_progress,
                        lang=st.session_state["lang"],
                    )
                    status.update(
                        label="✅ " + t("stage_completed"),
                        state="complete",
                        expanded=False,
                    )
                except Exception as e:
                    status.update(label="❌ Error", state="error", expanded=True)
                    st.error(f"Error: {e}")
                    result = None

            hint_placeholder.empty()
            progress_placeholder.empty()

            if result is not None:
                st.session_state.history.append({
                    "input": symptoms,
                    "result": result,
                })
                turn_no = len(st.session_state.history)
                render_result_turn(
                    t, result, symptoms, turn_no,
                    on_confirm_appointment=_confirm_appointment_cb,
                )
                st.rerun()

# Footer + 免责声明
if st.session_state.history:
    last_result = st.session_state.history[-1]["result"]
    lang = st.session_state["lang"]
    disclaimer_data = last_result.get("disclaimer", "")
    if isinstance(disclaimer_data, dict):
        disclaimer_text = (
            disclaimer_data.get("zh", "") if lang in ("zh-Hans", "zh-Hant")
            else disclaimer_data.get("en", "")
        )
    else:
        disclaimer_text = str(disclaimer_data) if disclaimer_data else ""

    if disclaimer_text:
        st.markdown(
            f'<div style="margin-top:2rem;padding:1rem 1.2rem;'
            f'background:#fef3c7;border-radius:10px;'
            f'border-left:4px solid #f59e0b;'
            f'color:#92400e;font-size:0.88rem;line-height:1.6;">'
            f'<strong>⚠️ {t("disclaimer")}</strong><br>'
            f'{disclaimer_text}</div>',
            unsafe_allow_html=True,
        )

st.markdown(
    f'<div class="footer">{t("footer")}</div>',
    unsafe_allow_html=True,
)