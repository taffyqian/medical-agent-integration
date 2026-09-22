"""全局 CSS"""
import streamlit as st


def inject_css():
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-family: -apple-system, "SF Pro Display", "PingFang SC",
                         "PingFang TC", "Microsoft YaHei", sans-serif;
        }
        .stApp { background: linear-gradient(180deg, #f5f9fc 0%, #eef4f8 100%); }
        [data-testid="stHeader"] { background: transparent; }

        .hero-title {
            font-size: 2.6rem; font-weight: 800;
            background: linear-gradient(90deg, #0e7490 0%, #14b8a6 60%, #22c55e 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; margin-bottom: 0.2rem; letter-spacing: -0.5px;
        }
        .hero-subtitle { color: #64748b; font-size: 1rem; margin-bottom: 1.5rem; }

        .card {
            background: #ffffff; border-radius: 14px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06),
                        0 4px 16px rgba(15, 23, 42, 0.04);
            margin-bottom: 1rem; border: 1px solid rgba(15, 23, 42, 0.04);
        }

        .greeting-card {
            background: linear-gradient(135deg, #ecfeff 0%, #f0fdfa 100%);
            border-left: 4px solid #14b8a6; border-radius: 12px;
            padding: 1.2rem 1.5rem; margin-bottom: 1.5rem;
        }
        .greeting-title { font-size: 1.3rem; font-weight: 700; color: #0f766e; }
        .greeting-sub { color: #475569; font-size: 0.92rem; margin-top: 0.3rem; }

        .badge {
            display: inline-block; padding: 0.25rem 0.75rem;
            border-radius: 999px; font-size: 0.78rem;
            font-weight: 600; letter-spacing: 0.3px;
        }
        .badge-emergency { background: #fee2e2; color: #b91c1c; }
        .badge-normal { background: #dcfce7; color: #15803d; }
        .badge-info { background: #e0f2fe; color: #0369a1; }

        .label {
            font-size: 0.78rem; color: #64748b; text-transform: uppercase;
            letter-spacing: 0.6px; font-weight: 600; margin-bottom: 0.25rem;
        }
        .value { font-size: 1rem; color: #0f172a; font-weight: 500; }

        .drug-card {
            background: #f8fafc; border-left: 4px solid #14b8a6;
            border-radius: 8px; padding: 1rem 1.2rem; margin: 0.6rem 0;
        }
        .drug-name { font-size: 1.1rem; font-weight: 700; color: #0f766e; }
        .drug-for { font-size: 0.85rem; color: #475569; margin-top: 0.25rem; }

        .fda-heading { color: #b91c1c; font-size: 0.95rem;
                       display: inline-block; margin-top: 0.5rem; }
        .fda-hl {
            background: #fef3c7; color: #92400e; padding: 0.05rem 0.25rem;
            border-radius: 4px; font-weight: 600;
        }
        .fda-content {
            background: #fffbeb; border-left: 3px solid #f59e0b;
            border-radius: 8px; padding: 1rem 1.2rem; font-size: 0.88rem;
            color: #44403c; line-height: 1.7; max-height: 500px; overflow-y: auto;
        }
        .fda-content ul { margin: 0.5rem 0 0.5rem 1rem; padding: 0; }
        .fda-content li { margin-bottom: 0.4rem; }

        .event-item {
            display: flex; align-items: center; padding: 0.5rem 0;
            border-bottom: 1px dashed #e2e8f0; font-size: 0.88rem;
        }
        .event-item:last-child { border-bottom: none; }
        .event-dot {
            width: 10px; height: 10px; border-radius: 50%;
            background: #14b8a6; margin-right: 0.75rem; flex-shrink: 0;
        }
        .event-stage { font-weight: 600; color: #334155; min-width: 130px; }
        .event-time {
            color: #94a3b8; font-size: 0.78rem;
            font-family: "SF Mono", Menlo, monospace;
        }

        .progress-step {
            display: flex; align-items: center; padding: 0.5rem 0;
            font-size: 0.92rem;
        }
        .progress-step-icon {
            width: 24px; text-align: center; margin-right: 0.75rem;
        }
        .progress-step.done { color: #15803d; }
        .progress-step.running { color: #0e7490; font-weight: 600; }
        .progress-step.waiting { color: #94a3b8; }

        .empty-state {
            text-align: center; padding: 3rem 2rem;
            background: #ffffff; border-radius: 14px;
            border: 1px dashed #cbd5e1;
        }
        .empty-title {
            font-size: 1.4rem; font-weight: 700; color: #0f766e;
            margin-bottom: 0.5rem;
        }
        .empty-desc { color: #64748b; margin-bottom: 1.5rem; }

        [data-testid="stSidebar"] {
            background: #ffffff; border-right: 1px solid #e2e8f0;
        }

        /* 主按钮：清晰的大按钮 */
        .stButton > button {
            border-radius: 10px; font-weight: 600;
            transition: all 0.15s ease;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #0e7490, #14b8a6) !important;
            color: #ffffff !important;
            border: none !important;
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            padding: 0.75rem 1.5rem !important;
            letter-spacing: 0.3px;
        }
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(20, 184, 166, 0.35);
        }
        .stButton > button[kind="primary"]:disabled {
            background: #e2e8f0 !important;
            color: #94a3b8 !important;
        }

        .stTextInput > div > div > input { border-radius: 8px; }

        .footer {
            text-align: center; color: #94a3b8;
            font-size: 0.78rem; padding: 2rem 0 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )