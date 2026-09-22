import uuid
import streamlit as st

from orchestrator import orchestrate
from ui_texts import make_translator
from ui_styles import inject_css
from ui_components import (
    render_sidebar,
    render_input_card,
    render_progress,
    render_result_turn,
)

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="Medical Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ============================================================
# 初始化 session state
# ============================================================
if "lang" not in st.session_state:
    st.session_state["lang"] = "zh-Hans"
if "session_id" not in st.session_state:
    st.session_state.session_id = f"sess_{uuid.uuid4().hex[:8]}"
    st.session_state.history = []
    st.session_state.greeted_name = None
if "symptoms_input" not in st.session_state:
    st.session_state.symptoms_input = ""
if "patient_name" not in st.session_state:
    st.session_state["patient_name"] = ""

# 翻译函数
t = make_translator(st)

# ============================================================
# 侧边栏
# ============================================================
render_sidebar(t)

# ============================================================
# 主区域标题
# ============================================================
st.markdown(
    f"""
    <div style="padding-top: 0.5rem;">
        <div class="hero-title">🏥 {t('title')}</div>
        <div class="hero-subtitle">{t('subtitle')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 问候语
# ============================================================
if st.session_state.history and st.session_state.greeted_name:
    st.markdown(
        f"""
        <div class="greeting-card">
            <div class="greeting-title">
                👋 {t('greeting', name=st.session_state.greeted_name)}
            </div>
            <div class="greeting-sub">{t('greeting_sub')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 输入卡片
# ============================================================
_, patient_name, analyze_clicked = render_input_card(t)

# ============================================================
# 处理分析
# ============================================================
if analyze_clicked and st.session_state.symptoms_input.strip():
    symptoms = [s.strip() for s in st.session_state.symptoms_input.split(",") if s.strip()]

    if patient_name and st.session_state.greeted_name != patient_name:
        st.session_state.greeted_name = patient_name

    progress_placeholder = st.empty()
    render_progress(t, None, progress_placeholder)

    def on_progress(stage: str):
        render_progress(t, stage, progress_placeholder)

    with st.spinner(t("analyzing")):
        result = orchestrate(
            st.session_state.session_id,
            symptoms,
            patient_name or None,
            progress_callback=on_progress,
        )

    render_progress(t, "__done__", progress_placeholder)

    st.session_state.history.append({
        "input": symptoms,
        "result": result,
    })
    st.session_state.symptoms_input = ""
    st.rerun()

# ============================================================
# 结果展示
# ============================================================
if not st.session_state.history:
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-title">{t('empty_title')}</div>
            <div class="empty-desc">{t('empty_desc')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(f"### {t('conversation')}")
    for idx, turn in enumerate(reversed(st.session_state.history), 1):
        turn_no = len(st.session_state.history) - idx + 1
        render_result_turn(t, turn["result"], turn["input"], turn_no)
# ============================================================
# 免责声明
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
            f"""
            <div style="margin-top: 2rem; padding: 1rem 1.2rem;
                        background: #fef3c7; border-radius: 10px;
                        border-left: 4px solid #f59e0b;
                        color: #92400e; font-size: 0.88rem;
                        line-height: 1.6;">
                <strong>⚠️ {t('disclaimer')}</strong><br>
                {disclaimer_text}
            </div>
            """,
            unsafe_allow_html=True,
        )
# ============================================================
# Footer
# ============================================================
st.markdown(f'<div class="footer">{t("footer")}</div>', unsafe_allow_html=True)