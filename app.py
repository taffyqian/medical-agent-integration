import uuid
import streamlit as st

from orchestrator import orchestrate
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
    page_icon="🏥",
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

# ============================================================
# 侧边栏
# ============================================================
render_sidebar(t)

# ============================================================
# 主标题
# ============================================================
st.markdown(
    f'<div class="hero-title">🏥 {t("title")}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="hero-subtitle">{t("subtitle")}</div>',
    unsafe_allow_html=True,
)

# ============================================================
# 空状态
# ============================================================
if not st.session_state.history:
    st.markdown(
        f'<div class="empty-state">'
        f'<div class="empty-title">{t("empty_title")}</div>'
        f'<div class="empty-desc">{t("empty_desc")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# 显示历史对话
# ============================================================
for i, turn in enumerate(st.session_state.history):
    with st.chat_message("user"):
        st.markdown(f"{', '.join(turn['input'])}")
    with st.chat_message("assistant"):
        render_result_turn(t, turn["result"], turn["input"], i + 1)

# ============================================================
# 对话总结（多轮之后；最后一轮是紧急时仍显示，但会标红）
# ============================================================
if len(st.session_state.history) >= 2:
    # 用标准化症状（从最新 state 读）
    all_symptoms = (
        st.session_state.history[-1]["result"]
        .get("state", {})
        .get("symptoms_history", [])
    )

    # 汇总所有推荐药品（去重）
    all_drugs = []
    for turn in st.session_state.history:
        for rec in turn["result"].get("recommendations", []):
            dn = rec.get("drug_name", "")
            if dn and dn not in all_drugs:
                all_drugs.append(dn)

    # 汇总可能原因（严格去重：忽略大小写 + 首尾空格）
    all_causes = []
    seen_causes = set()
    for turn in st.session_state.history:
        for c in turn["result"].get("possible_causes", []):
            cond = c.get("condition", "").strip()
            key = cond.lower()
            if cond and key not in seen_causes:
                all_causes.append(cond)
                seen_causes.add(key)
    # 限制最多 5 个，避免总结卡片过长
    all_causes = all_causes[:5]

    # 计算"最高严重程度" + 紧急症状列表
    all_severities = []
    emergency_symptoms = []
    for turn in st.session_state.history:
        r = turn["result"]
        if r.get("action") == "emergency_escalation":
            all_severities.append("emergency")
            matched = r.get("matched", [])
            if matched:
                emergency_symptoms.extend(matched)
        else:
            all_severities.append(r.get("severity", "mild"))

    severity_rank = {"emergency": 2, "moderate": 1, "mild": 0, "non-emergency": 0}
    if all_severities:
        latest_severity = max(all_severities, key=lambda s: severity_rank.get(s, 0))
    else:
        latest_severity = "-"

    # 最新预约
    latest = st.session_state.history[-1]["result"]
    latest_appt = latest.get("appointment", {})
    appt_time = ""
    if latest_appt.get("scheduled"):
        appt_time = format_local_time(
            latest_appt.get("slot_utc", ""), st.session_state["lang"]
        )

    # 拼 HTML
    sev_color = "#b91c1c" if latest_severity == "emergency" else "#15803d"
    drugs_str = " · ".join([
        display_drug_name(d, st.session_state["lang"]) for d in all_drugs
    ]) or "-"
    causes_str = " · ".join(all_causes) or "-"

    # 严重程度显示文本（含紧急症状说明）
    severity_display = latest_severity
    if emergency_symptoms:
        unique_emerg = list(set(emergency_symptoms))
        severity_display = f'{latest_severity} ({t("includes_emergency")}: {" · ".join(unique_emerg)})'

    sum_html = (
        '<div style="background:#ffffff;border:1px solid #cbd5e1;'
        'border-radius:12px;padding:1rem 1.3rem;margin-top:2rem;'
        'margin-bottom:1rem;font-size:0.88rem;color:#334155;">'
        # 标题
        f'<div style="display:flex;align-items:center;gap:0.5rem;'
        f'margin-bottom:0.7rem;font-weight:700;color:#0f172a;'
        f'font-size:0.95rem;">'
        f'<span>📋</span><span>{t("conversation_summary")}</span>'
        f'</div>'
        # 症状
        f'<div style="margin-bottom:0.35rem;">'
        f'<span style="color:#94a3b8;font-weight:600;'
        f'min-width:80px;display:inline-block;">'
        f'{t("summary_symptoms")}</span>'
        + " · ".join(all_symptoms) +
        f'</div>'
        # 严重程度（最高档 + 紧急症状）
        f'<div style="margin-bottom:0.35rem;">'
        f'<span style="color:#94a3b8;font-weight:600;'
        f'min-width:80px;display:inline-block;">'
        f'{t("summary_severity")}</span>'
        f'<span style="color:{sev_color};font-weight:600;">'
        f'{severity_display}'
        f'</span>'
        f'</div>'
        # 可能原因
        f'<div style="margin-bottom:0.35rem;">'
        f'<span style="color:#94a3b8;font-weight:600;'
        f'min-width:80px;display:inline-block;">'
        f'{t("summary_causes")}</span>'
        f'{causes_str}'
        f'</div>'
        # 药品
        f'<div style="margin-bottom:0.35rem;">'
        f'<span style="color:#94a3b8;font-weight:600;'
        f'min-width:80px;display:inline-block;">'
        f'{t("summary_drugs")}</span>'
        f'{drugs_str}'
        f'</div>'
    )
    # 预约
    if appt_time:
        sum_html += (
            f'<div style="margin-bottom:0;">'
            f'<span style="color:#94a3b8;font-weight:600;'
            f'min-width:80px;display:inline-block;">'
            f'{t("summary_appointment")}</span>'
            f'{appt_time}'
            f'</div>'
        )
    sum_html += '</div>'
    st.markdown(sum_html, unsafe_allow_html=True)

# ============================================================
# 追问提示（底部聊天框上方）
# ============================================================
if st.session_state.history:
    last_result = st.session_state.history[-1]["result"]
    last_fqs = last_result.get("_followup_questions", [])

    if last_fqs:
        # 分隔线
        st.markdown(
            '<div style="'
            'margin-top: 2rem;'
            'margin-bottom: 1rem;'
            'border-top: 1px solid #e2e8f0;'
            '"></div>',
            unsafe_allow_html=True,
        )

        # 小标签
        st.markdown(
            f'<div style="'
            f'font-size:0.75rem;'
            f'color:#94a3b8;'
            f'font-weight:500;'
            f'letter-spacing:0.4px;'
            f'margin-bottom:0.4rem;'
            f'">{t("followup_prompt")}</div>',
            unsafe_allow_html=True,
        )

        # 纯列表
        list_html = '<ul style="list-style:none;padding:0;margin:0 0 1rem 0;">'
        for q in last_fqs:
            list_html += (
                f'<li style="'
                f'font-size:0.9rem;'
                f'color:#475569;'
                f'line-height:1.7;'
                f'padding:0.1rem 0;'
                f'">'
                f'· {q}'
                f'</li>'
            )
        list_html += '</ul>'
        st.markdown(list_html, unsafe_allow_html=True)

# ============================================================
# 底部聊天输入框
# ============================================================
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
                    )
                    status.update(
                        label="✅ " + t("stage_completed"),
                        state="complete",
                        expanded=False,
                    )
                except Exception as e:
                    status.update(
                        label="❌ Error",
                        state="error",
                        expanded=True,
                    )
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
                render_result_turn(t, result, symptoms, turn_no)
                st.rerun()

# ============================================================
# Footer + 免责声明
# ============================================================
if st.session_state.history:
    last_result = st.session_state.history[-1]["result"]
    disclaimer_data = last_result.get("disclaimer", {})
    lang = st.session_state["lang"]
    disclaimer_text = (
        disclaimer_data.get("zh", "") if lang in ("zh-Hans", "zh-Hant")
        else disclaimer_data.get("en", "")
    )
    if disclaimer_text:
        st.markdown(
            f'<div style="margin-top:2rem;padding:1rem 1.2rem;'
            f'background:#fef3c7;border-radius:10px;'
            f'border-left:4px solid #f59e0b;'
            f'color:#92400e;font-size:0.88rem;line-height:1.6;">'
            f'<strong>⚠️ {t("disclaimer")}</strong><br>'
            f'{disclaimer_text}'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown(
    f'<div class="footer">{t("footer")}</div>',
    unsafe_allow_html=True,
)
