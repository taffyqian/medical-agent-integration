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

        /* ===== 侧边栏：极浅灰，与主面板区分 ===== */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 1px solid #e5e7eb;
        }
        [data-testid="stSidebar"] .card { padding: 0.85rem 1rem; }

        .hero-title {
            font-size: 1.9rem; font-weight: 800; color: #0a0a0a;
            margin-bottom: 0.35rem; letter-spacing: -0.6px;
        }
        .hero-subtitle {
            color: #71717a; font-size: 0.9rem;
            margin-bottom: 2rem; line-height: 1.55;
        }

        /* ===== 卡片：统一圆角 12px ===== */
        .card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.3rem 1.5rem;
            margin-bottom: 1rem;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px !important;
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
            border-radius: 12px !important;
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

        /* ===== 按钮 ===== */
        .stButton > button {
            border-radius: 8px; font-weight: 500;
            transition: all 0.15s ease;
            border: 1px solid #e5e7eb;
            color: #52525b;
            background: #ffffff;
            font-size: 0.86rem;
            padding: 0.5rem 1rem;
        }
        .stButton > button:hover {
            border-color: #d4d4d8;
            background: #fafafa;
            color: #18181b;
        }
        /* 主按钮：医疗蓝（信任感） */
        .stButton > button[kind="primary"] {
            background: #2563eb !important;
            color: #ffffff !important;
            border: 1px solid #2563eb !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            padding: 0.55rem 1rem !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.2) !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: #1d4ed8 !important;
            border-color: #1d4ed8 !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
            transform: translateY(-1px);
        }
        .stButton > button[kind="primary"]:disabled {
            background: #f4f4f5 !important; color: #a1a1aa !important;
            border-color: #e5e7eb !important;
            box-shadow: none !important;
            transform: none;
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

        /* ===== 进度条 ===== */
        .progress-row {
            display: flex; align-items: center; gap: 0.5rem;
            padding: 0.2rem 0; flex-wrap: wrap;
            position: relative;
        }
        .progress-chip {
            display: inline-flex; align-items: center; gap: 0.35rem;
            padding: 0.28rem 0.7rem; border-radius: 999px;
            font-size: 0.76rem; font-weight: 600;
            border: 1px solid #e5e7eb; background: #ffffff;
            color: #71717a;
            transition: all 0.2s ease;
            position: relative;
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
        @keyframes pulse-ring {
            0% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.5); transform: scale(1); }
            70% { box-shadow: 0 0 0 8px rgba(79, 70, 229, 0); transform: scale(1.05); }
            100% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); transform: scale(1); }
        }
        .progress-chip.running .progress-dot {
            animation: pulse-ring 1.8s ease-in-out infinite;
            background: #4f46e5;
            width: 7px; height: 7px;
        }
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.15); }
            50% { box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12); }
        }
        .progress-chip.running { animation: glow 2s ease-in-out infinite; }
        .progress-chip.done .progress-dot {
            background: #10b981; width: 6px; height: 6px;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
        }
        .progress-chip + .progress-chip::before {
            content: ""; position: absolute;
            left: -12px; top: 50%; transform: translateY(-50%);
            width: 8px; height: 2px;
            background: #e5e7eb; border-radius: 1px;
        }
        .progress-chip.done + .progress-chip::before { background: #a7f3d0; }
        .progress-chip.done + .progress-chip.running::before {
            background: linear-gradient(90deg, #a7f3d0 0%, #c7d2fe 100%);
        }
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        .progress-shimmer {
            height: 2px; margin-top: 0.6rem; border-radius: 999px;
            background: linear-gradient(90deg, transparent 0%,
                rgba(79, 70, 229, 0.4) 50%, transparent 100%);
            background-size: 200% 100%;
            animation: shimmer 2.5s linear infinite;
        }

        /* ===== 聊天气泡 ===== */
        [data-testid="stChatMessage"] {
            border-radius: 12px !important;
            padding: 0.8rem 1.1rem !important;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            margin-bottom: 0.6rem !important;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            background: #eff6ff;
            border-color: #bfdbfe;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
            background: #ffffff;
        }
        [data-testid="stChatMessageAvatarUser"],
        [data-testid="stChatMessageAvatarAssistant"] {
            border-radius: 50% !important;
            overflow: hidden !important;
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
            border-radius: 12px !important;
            border: 1px solid #e5e7eb !important;
            background: #ffffff !important;
        }
        [data-testid="stExpander"] details > summary {
            padding: 0.7rem 1rem !important;
            font-weight: 600 !important;
            color: #27272a !important;
            border-radius: 12px !important;
        }
        [data-testid="stExpander"] details[open] > summary {
            border-bottom: 1px solid #f4f4f5 !important;
            border-radius: 12px 12px 0 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )