"""全局 CSS"""
import streamlit as st


def inject_css():
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-family: -apple-system, "SF Pro Text", "Inter",
                         "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        .stApp { background-color: #fafafa; }
        [data-testid="stHeader"] { background: transparent; }

        .hero-title {
            font-size: 1.9rem; font-weight: 800; color: #0a0a0a;
            margin-bottom: 0.35rem; letter-spacing: -0.6px;
        }
        .hero-subtitle {
            color: #71717a; font-size: 0.9rem;
            margin-bottom: 2rem; line-height: 1.55;
        }

        .card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.3rem 1.5rem;
            margin-bottom: 1rem;
        }

        .badge {
            display: inline-block; padding: 0.2rem 0.55rem;
            border-radius: 6px; font-size: 0.72rem; font-weight: 600;
            letter-spacing: 0.2px;
        }
        .badge-emergency { background: #fee2e2; color: #991b1b; }
        .badge-normal { background: #ecfdf5; color: #065f46; }
        .badge-info { background: #eef2ff; color: #3730a3; }

        .label {
            font-size: 0.72rem; color: #71717a;
            text-transform: uppercase; letter-spacing: 0.5px;
            font-weight: 600; margin-bottom: 0.2rem;
        }
        .value {
            font-size: 0.92rem; color: #18181b; font-weight: 500;
        }

        .drug-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.1rem 1.3rem;
            margin: 0.7rem 0;
            display: flex; flex-direction: column; gap: 0.35rem;
        }
        .drug-name { font-size: 1.05rem; font-weight: 700; color: #18181b; }
        .drug-for { font-size: 0.84rem; color: #52525b; }
        .drug-for strong { color: #0d9488; font-weight: 600; }

        .fda-heading {
            color: #92400e !important;
            font-size: 0.88rem !important;
            font-weight: 700 !important;
            display: inline-block;
        }
        .fda-content {
            background: #fffbeb !important;
            border: 1px solid #fef3c7 !important;
            border-left: 3px solid #f59e0b !important;
            border-radius: 10px !important;
            padding: 1rem 1.2rem !important;
            font-size: 0.86rem !important;
            color: #451a03 !important;
            line-height: 1.65 !important;
        }
        .fda-content > div:first-child { margin-top: 0 !important; }
        .fda-content ul {
            margin: 0.4rem 0 0.6rem 1.1rem !important;
            padding: 0 !important;
        }
        .fda-content li {
            margin-bottom: 0.3rem !important;
            color: #57534e !important;
        }

        [data-testid="stSidebar"] {
            background-color: #ffffff; border-right: 1px solid #e5e7eb;
        }
        [data-testid="stSidebar"] .card { padding: 0.85rem 1rem; }

        .stButton > button {
            border-radius: 8px; font-weight: 600;
            transition: all 0.15s ease;
            border: 1px solid #d4d4d8;
            color: #18181b;
            background: #ffffff;
        }
        .stButton > button:hover {
            border-color: #a1a1aa; background: #f4f4f5;
        }
        .stButton > button[kind="primary"] {
            background: #ffffff !important;
            color: #4f46e5 !important;
            border: 1px solid #c7d2fe !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            padding: 0.5rem 1rem !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: #eef2ff !important;
            border-color: #4f46e5 !important;
            color: #4338ca !important;
        }
        .stButton > button[kind="primary"]:disabled {
            background: #fafafa !important; color: #a1a1aa !important;
            border-color: #e5e7eb !important;
        }
        .stTextInput > div > div > input { border-radius: 8px; }

        .event-item {
            display: flex; align-items: center; padding: 0.5rem 0;
            border-bottom: 1px dashed #e5e7eb; font-size: 0.86rem;
        }
        .event-item:last-child { border-bottom: none; }
        .event-dot {
            width: 6px; height: 6px; border-radius: 50%;
            background: #4f46e5; margin-right: 0.75rem; flex-shrink: 0;
        }
        .event-stage { font-weight: 600; color: #27272a; min-width: 140px; }
        .event-time {
            color: #a1a1aa; font-size: 0.76rem;
            font-family: "SF Mono", Menlo, monospace;
        }

        .progress-row {
            display: flex; align-items: center; gap: 0.5rem;
            padding: 0.2rem 0; flex-wrap: wrap;
        }
        .progress-chip {
            display: inline-flex; align-items: center; gap: 0.35rem;
            padding: 0.28rem 0.7rem; border-radius: 999px;
            font-size: 0.76rem; font-weight: 600;
            border: 1px solid #e5e7eb; background: #ffffff;
            color: #71717a;
            transition: all 0.2s ease;
        }
        .progress-chip.done {
            background: #ecfdf5; border-color: #d1fae5; color: #065f46;
        }
        .progress-chip.running {
            background: #eef2ff; border-color: #c7d2fe; color: #3730a3;
            font-weight: 700;
        }
        .progress-chip.waiting {
            background: #fafafa; border-color: #e5e7eb; color: #a1a1aa;
        }
        .progress-dot {
            width: 5px; height: 5px; border-radius: 50%;
            background: currentColor; opacity: 0.9;
        }

        .empty-state {
            text-align: center; padding: 3.5rem 2rem;
            background: #ffffff; border: 1px dashed #d4d4d8;
            border-radius: 12px;
        }
        .empty-title {
            font-size: 1.25rem; font-weight: 800; color: #0a0a0a;
            margin-bottom: 0.5rem; letter-spacing: -0.3px;
        }
        .empty-desc { color: #71717a; font-size: 0.88rem; line-height: 1.6; }

        .footer {
            text-align: center; color: #a1a1aa;
            font-size: 0.76rem; padding: 2.5rem 0 1.5rem 0;
            letter-spacing: 0.3px;
        }

        [data-testid="stExpander"] { margin-bottom: 1rem !important; }
        [data-testid="stExpander"] details {
            border-radius: 10px !important;
            border: 1px solid #e5e7eb !important;
            background: #ffffff !important;
        }
        [data-testid="stExpander"] details > summary {
            padding: 0.7rem 1rem !important;
            font-weight: 600 !important;
            color: #27272a !important;
            border-radius: 10px !important;
        }
        [data-testid="stExpander"] details[open] > summary {
            border-bottom: 1px solid #f4f4f5 !important;
            border-radius: 10px 10px 0 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
