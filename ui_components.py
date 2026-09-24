"""UI 组件：侧边栏、进度条、结果卡片"""
import streamlit as st

from ui_texts import QUICK_SYMPTOMS, display_drug_name
from ui_helpers import format_local_time, format_fda_warnings


# ============================================================
# 侧边栏
# ============================================================
def render_sidebar(t):
    with st.sidebar:
        lang_options = {"zh-Hans": "简体中文", "zh-Hant": "繁體中文", "en": "English"}
        selected_lang = st.radio(
            t("lang_label"),
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=list(lang_options.keys()).index(st.session_state["lang"]),
            key="lang_radio",
        )
        if selected_lang != st.session_state["lang"]:
            st.session_state["lang"] = selected_lang
            st.rerun()

        st.divider()
        st.markdown(f"### {t('sidebar_title')}")

        session_html = (
            f'<div class="card">'
            f'<div class="label">{t("session_id")}</div>'
            f'<div class="value" style="font-family:SF Mono,Menlo,monospace;'
            f'font-size:0.82rem;word-break:break-all;color:#52525b;">'
            f'{st.session_state.session_id}</div>'
            f'</div>'
        )
        st.markdown(session_html, unsafe_allow_html=True)

        if st.button(t("new_session"), use_container_width=True):
            import uuid
            st.session_state.session_id = f"sess_{uuid.uuid4().hex[:8]}"
            st.session_state.history = []
            st.session_state.greeted_name = None
            st.session_state.symptoms_input = ""
            st.rerun()

        st.divider()

        if st.session_state.get("history"):
            last = st.session_state.history[-1]["result"]
            state = last["state"]
            st.markdown(f"**{t('symptoms_history')}**")
            for s in state["symptoms_history"]:
                st.markdown(f"- `{s}`")

            badge_cls = "badge-emergency" if state.get("severity") == "emergency" else "badge-normal"
            status_html = (
                f'<div style="margin-top:0.8rem;">'
                f'<div class="label">{t("most_recent")}</div>'
                f'<div class="value">{state.get("most_recent_symptom", "-")}</div>'
                f'</div>'
                f'<div style="margin-top:0.7rem;">'
                f'<div class="label">{t("severity")}</div>'
                f'<span class="badge {badge_cls}">{state.get("severity", "-")}</span>'
                f'</div>'
                f'<div style="margin-top:0.7rem;">'
                f'<div class="label">{t("workflow_stage")}</div>'
                f'<span class="badge badge-info">{state.get("workflow_stage", "-")}</span>'
                f'</div>'
            )
            st.markdown(status_html, unsafe_allow_html=True)
        else:
            st.caption(t("no_state"))


# ============================================================
# 进度条：横向 chip + 动画
# ============================================================
def render_progress(t, current_stage, placeholder):
    stage_labels = {
        "emergency_check": t("stage_emergency_check"),
        "symptom_analysis": t("stage_symptom_analysis"),
        "drug_lookup": t("stage_drug_lookup"),
        "appointment": t("stage_appointment"),
    }
    stage_order = ["emergency_check", "symptom_analysis", "drug_lookup", "appointment"]

    if current_stage is None:
        idx_current = -1
    elif current_stage == "__done__":
        idx_current = len(stage_order)
    elif current_stage in stage_order:
        idx_current = stage_order.index(current_stage)
    else:
        idx_current = -1

    chips = ""
    for idx_stage, stage in enumerate(stage_order):
        label = stage_labels[stage]
        if idx_stage < idx_current:
            cls = "done"
        elif idx_stage == idx_current:
            cls = "running"
        else:
            cls = "waiting"
        chips += (
            f'<div class="progress-chip {cls}">'
            f'<span class="progress-dot"></span>'
            f'<span>{label}</span></div>'
        )

    show_shimmer = (current_stage is not None and current_stage != "__done__")
    shimmer_html = '<div class="progress-shimmer"></div>' if show_shimmer else ''

    html = (
        f'<div class="card" style="padding:0.85rem 1.1rem;">'
        f'<div class="label" style="margin-bottom:0.5rem;">'
        f'{t("progress_heading")}</div>'
        f'<div class="progress-row">{chips}</div>'
        f'{shimmer_html}'
        f'</div>'
    )
    placeholder.markdown(html, unsafe_allow_html=True)


# ============================================================
# 结果卡片
# ============================================================
def render_result_turn(t, r, turn_input, turn_no, on_confirm_appointment=None):
    with st.expander(
        f"{t('turn', n=turn_no)}  ·  {', '.join(turn_input)}",
        expanded=(turn_no == len(st.session_state.get("history", []))),
    ):
        # ---------- 紧急分支 ----------
        if r["action"] == "emergency_escalation":
            lang = st.session_state["lang"]
            if lang == "zh-Hant":
                hotline_main = "請立即撥打當地急救電話"
                hotline_numbers = "999（香港）· 119（台灣）· 120（中國內地）· 112（歐盟）"
            elif lang == "en":
                hotline_main = "Call your local emergency services immediately"
                hotline_numbers = "911 (US) · 999 (UK/HK) · 120 (China) · 112 (EU)"
            else:
                hotline_main = "请立即拨打当地急救电话"
                hotline_numbers = "120（中国内地）· 999（香港）· 119（台湾）· 112（欧盟）"

            matched_str = " · ".join(r.get("normalized") or r.get("matched") or [])
            emergency_html = (
                f'<div style="'
                f'background:#ffffff;'
                f'border:1px solid #e5e7eb;'
                f'border-top:3px solid #dc2626;'
                f'border-radius:12px;'
                f'padding:1.3rem 1.5rem;'
                f'margin-top:0.6rem;">'

                f'<div style="display:inline-block;'
                f'background:#ffffff;'
                f'color:#b91c1c;'
                f'border:1px solid #fecaca;'
                f'font-size:0.7rem;'
                f'font-weight:800;'
                f'letter-spacing:1.8px;'
                f'padding:0.25rem 0.7rem;'
                f'border-radius:6px;'
                f'text-transform:uppercase;">'
                f'{t("emergency")}</div>'

                f'<div style="margin-top:0.95rem;'
                f'font-size:1rem;'
                f'font-weight:600;'
                f'color:#3f3f46;'
                f'line-height:1.6;">'
                f'{t("emergency_msg")}</div>'

                f'<div style="margin-top:1.3rem;'
                f'background:linear-gradient(180deg, #ffffff 0%, #fff5f5 100%);'
                f'border:1px solid #fee2e2;'
                f'border-radius:14px;'
                f'padding:1.4rem 1.6rem;'
                f'text-align:center;'
                f'box-shadow:0 8px 24px rgba(220,38,38,0.08), '
                f'0 2px 6px rgba(0,0,0,0.03);">'

                f'<div style="display:flex;align-items:center;'
                f'justify-content:center;gap:0.6rem;'
                f'margin-bottom:0.7rem;">'
                f'<span style="font-size:1.6rem;">📞</span>'
                f'<span style="font-size:1.35rem;'
                f'font-weight:800;'
                f'color:#b91c1c;'
                f'letter-spacing:0.2px;">'
                f'{hotline_main}</span></div>'

                f'<div style="font-size:1.15rem;'
                f'font-weight:700;'
                f'color:#b91c1c;'
                f'letter-spacing:0.6px;'
                f'font-family:SF Mono,Menlo,monospace;">'
                f'{hotline_numbers}</div>'

                f'</div>'

                f'<div style="margin-top:1rem;'
                f'display:grid;'
                f'grid-template-columns:110px 1fr;'
                f'gap:0.4rem 1rem;'
                f'font-size:0.86rem;">'
                f'<div style="color:#71717a;'
                f'font-weight:700;'
                f'text-transform:uppercase;'
                f'font-size:0.68rem;'
                f'letter-spacing:0.6px;'
                f'padding-top:0.15rem;">'
                f'{t("matched")}</div>'
                f'<div style="color:#18181b;font-weight:500;">'
                f'{matched_str}</div>'
                f'</div></div>'
            )
            st.markdown(emergency_html, unsafe_allow_html=True)

        # ---------- 非紧急分支 ----------
        else:
            sev = r.get("severity", "-")
            st.markdown(
                f'<div class="card" style="padding:0.75rem 1.2rem;'
                f'display:flex;align-items:center;gap:0.7rem;">'
                f'<span class="badge badge-normal">{t("non_emergency")}</span>'
                f'<span class="label" style="margin:0;">{t("severity")}:</span>'
                f'<span class="value">{sev}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # 可能原因（深灰标题栏 + 与医疗建议同字号）
            possible_causes = r.get("possible_causes", [])
            if possible_causes:
                likelihood_label = {
                    "common": t("cause_common"),
                    "possible": t("cause_possible"),
                    "less common": t("cause_less_common"),
                }
                likelihood_color = {
                    "common": "#0d9488",
                    "possible": "#14b8a6",
                    "less common": "#71717a",
                }
                cause_rows = ""
                for c in possible_causes:
                    condition = c.get("condition", "")
                    likelihood = c.get("likelihood", "possible")
                    note = c.get("note", "")
                    color = likelihood_color.get(likelihood, "#71717a")
                    lbl = likelihood_label.get(likelihood, likelihood)
                    if condition:
                        cause_rows += (
                            f'<div style="display:flex;gap:0.9rem;'
                            f'align-items:flex-start;padding:0.55rem 0.9rem;'
                            f'margin-bottom:0.35rem;background:#fafafa;'
                            f'border-radius:8px;">'
                            f'<div style="flex-shrink:0;min-width:58px;'
                            f'font-size:0.68rem;font-weight:600;color:{color};'
                            f'padding-top:0.15rem;letter-spacing:0.2px;">'
                            f'{lbl}</div>'
                            f'<div style="font-size:0.82rem;'
                            f'color:#18181b;line-height:1.55;">'
                            f'<span style="font-weight:500;">{condition}</span>'
                            + (f' <span style="color:#71717a;font-weight:400;">— {note}</span>' if note else "") +
                            f'</div></div>'
                        )
                cause_html = (
                    '<div class="card" style="padding:0;margin-top:0.8rem;overflow:hidden;">'
                    '<div style="padding:0.7rem 1.1rem;'
                    'display:flex;align-items:center;gap:0.5rem;'
                    'background:#e2e8f0;'
                    'border-bottom:1px solid #cbd5e1;">'
                    '<span style="font-size:0.9rem;">🔍</span>'
                    '<span style="font-size:0.72rem;font-weight:700;'
                    'color:#334155;letter-spacing:0.8px;text-transform:uppercase;">'
                    + t("possible_causes") + '</span></div>'
                    '<div style="padding:0.8rem 0.9rem;">' + cause_rows + '</div>'
                    '<div style="padding:0.6rem 1.1rem;background:#fffbeb;'
                    'border-top:1px solid #fef3c7;font-size:0.76rem;'
                    'color:#92400e;">' + t("cause_disclaimer") + '</div></div>'
                )
                st.markdown(cause_html, unsafe_allow_html=True)

            # 推荐药品 + 医疗建议（合并为一张大卡片）
            recs = r.get("recommendations", [])
            if recs:
                # ---- 大卡片开始 ----
                card_parts = []
                card_parts.append(
                    '<div class="card" style="padding:0;margin-top:1.2rem;overflow:hidden;">'
                )
                # 顶层标题（推荐药品与医疗建议）
                card_parts.append(
                    '<div style="padding:0.8rem 1.2rem;'
                    'background:#e2e8f0;border-bottom:1px solid #cbd5e1;'
                    'display:flex;align-items:center;gap:0.5rem;">'
                    '<span style="font-size:1rem;">💊</span>'
                    '<span style="font-size:0.78rem;font-weight:700;'
                    'color:#334155;letter-spacing:0.8px;text-transform:uppercase;">'
                    + t("drugs") + '</span></div>'
                )
                # 药品内容区
                card_parts.append('<div style="padding:0.9rem 1.1rem;">')

                all_questions = []
                advice_html_global = ""   # 收集医疗建议（按第一个药品为准）

                for idx, rec in enumerate(recs):
                    info = rec.get("drug_info", {})
                    brand = info.get("brand_name", "-") if info.get("ok") else "-"
                    for_syms = ", ".join(rec.get("symptoms", []))
                    display_name = display_drug_name(rec["drug_name"], st.session_state["lang"])

                    otc_tag = ""
                    if rec.get("is_otc"):
                        otc_tag = (
                            f'<span style="font-size:0.68rem;font-weight:700;'
                            f'color:#0d9488;border:1px solid #d1fae5;'
                            f'padding:0.08rem 0.4rem;border-radius:4px;'
                            f'letter-spacing:0.5px;margin-left:0.5rem;">'
                            f'{t("otc_label")}</span>'
                        )

                    # 药品子卡（浅灰底圆角，放在大卡片内部）
                    card_parts.append(
                        f'<div style="background:#fafafa;border-radius:10px;'
                        f'padding:0.85rem 1rem;margin-bottom:0.6rem;">'
                        f'<div style="display:flex;align-items:center;'
                        f'font-size:1rem;font-weight:700;color:#18181b;">'
                        f'<span>{display_name}</span>{otc_tag}</div>'
                        f'<div style="font-size:0.82rem;color:#52525b;'
                        f'margin-top:0.3rem;">'
                        f'<strong style="color:#0d9488;">{t("for_symptoms")}</strong>: {for_syms}'
                        f'</div>'
                        f'<div style="font-size:0.82rem;color:#52525b;'
                        f'margin-top:0.2rem;">'
                        f'<strong style="color:#0d9488;">{t("brand")}</strong>: {brand}'
                        f'</div></div>'
                    )

                    # 收集医疗建议（只用第一个药品的建议）
                    if idx == 0:
                        advice_rows = []
                        if rec.get("usage_advice"):
                            advice_rows.append((t("usage_advice"), rec["usage_advice"]))
                        if rec.get("self_care"):
                            advice_rows.append((t("self_care"), rec["self_care"]))
                        if rec.get("when_to_seek_help"):
                            advice_rows.append((t("when_to_seek_help"), rec["when_to_seek_help"]))
                        if advice_rows:
                            advice_html_global += (
                                '<div style="margin-top:1rem;padding-top:1rem;'
                                'border-top:1px solid #e5e7eb;">'
                                '<div style="display:flex;align-items:center;gap:0.5rem;'
                                'margin-bottom:0.6rem;">'
                                '<span style="font-size:0.95rem;">💡</span>'
                                '<span style="font-size:0.76rem;font-weight:700;'
                                'color:#334155;letter-spacing:0.8px;text-transform:uppercase;">'
                                + t("medical_guidance") + '</span></div>'
                            )
                            for label, text in advice_rows:
                                advice_html_global += (
                                    f'<div style="display:flex;gap:0.9rem;'
                                    f'align-items:flex-start;background:#fafafa;'
                                    f'border-radius:8px;padding:0.6rem 0.9rem;'
                                    f'margin-bottom:0.35rem;">'
                                    f'<div style="flex-shrink:0;min-width:70px;'
                                    f'font-size:0.78rem;font-weight:700;color:#71717a;">'
                                    f'{label}</div>'
                                    f'<div style="font-size:0.82rem;color:#18181b;'
                                    f'line-height:1.6;">{text}</div>'
                                    f'</div>'
                                )
                            advice_html_global += '</div>'

                    # 收集追问
                    for q in rec.get("followup_questions", []):
                        if q and q not in all_questions:
                            all_questions.append(q)

                    # FDA 折叠（每个药品一个）
                    if info.get("ok") and info.get("warnings"):
                        with st.expander(t('view_warnings')):
                            formatted = format_fda_warnings(info["warnings"], st.session_state["lang"])
                            st.markdown(f'<div class="fda-content">{formatted}</div>',
                                        unsafe_allow_html=True)
                    elif not info.get("ok"):
                        st.caption(t("no_fda"))

                # 关闭药品内容区
                card_parts.append(advice_html_global)
                card_parts.append('</div></div>')  # 药品内容区 + 大卡片

                st.markdown("".join(card_parts), unsafe_allow_html=True)

                if all_questions:
                    r["_followup_questions"] = all_questions

            # 预约确认
            if r.get("pending_appointment") and turn_no == len(st.session_state.get("history", [])):
                _render_appointment_ui(t, r, turn_no, on_confirm_appointment)

            # 已预约展示
            appt = r.get("appointment", {})
            if appt and appt.get("scheduled"):
                local_time = format_local_time(appt.get("slot_utc", ""), st.session_state["lang"])
                st.markdown(
                    f'<div class="card" style="padding:0.8rem 1.1rem;'
                    f'display:flex;align-items:center;gap:0.7rem;">'
                    f'<span class="label" style="margin:0;">{t("appointment")}</span>'
                    f'<span class="value" style="font-family:SF Mono,Menlo,monospace;">'
                    f'{local_time}</span></div>',
                    unsafe_allow_html=True,
                )

        # 事件流
        with st.expander(t('event_log')):
            events_html = '<div class="card" style="padding:0.75rem 1rem;">'
            for event in r["state"]["events"]:
                stage_label = t(f"stage_{event['stage']}")
                time_str = event["at"].replace("T", " ")[:19]
                events_html += (
                    f'<div class="event-item">'
                    f'<div class="event-dot"></div>'
                    f'<div class="event-stage">{stage_label}</div>'
                    f'<div class="event-time">{time_str}</div>'
                    f'</div>'
                )
            events_html += "</div>"
            st.markdown(events_html, unsafe_allow_html=True)


# ============================================================
# 预约 UI（状态机）
# 白底 + 5px 靛蓝粗条 + 强阴影 —— 国际 SaaS "行动卡片"风格
# ============================================================
def _render_appointment_ui(t, r, turn_no, on_confirm_appointment):
    state_key = f"appt_state_{turn_no}"
    date_key = f"appt_date_{turn_no}"
    time_key = f"appt_time_{turn_no}"
    result_key = f"appt_result_{turn_no}"

    if state_key not in st.session_state:
        st.session_state[state_key] = "asking"

    current = st.session_state[state_key]

    # 状态 1: 询问（白底 + 5px 靛蓝粗条 + 强阴影）
    if current == "asking":
        st.markdown(
            f'<div style="margin-top:1.3rem;margin-bottom:0.6rem;'
            f'padding:1.2rem 1.4rem;'
            f'background:#ffffff;'
            f'border:1px solid #cbd5e1;'
            f'border-left:5px solid #4f46e5;'
            f'border-radius:12px;'
            f'box-shadow:0 8px 24px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04);">'
            f'<div style="display:flex;align-items:center;gap:0.7rem;">'
            f'<span style="font-size:1.4rem;">🩺</span>'
            f'<span style="font-size:1.05rem;font-weight:800;color:#0a0a0a;'
            f'letter-spacing:-0.2px;">'
            f'{t("ask_appointment")}</span></div></div>',
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("yes"), key=f"appt_yes_{turn_no}",
                         use_container_width=True, type="primary"):
                st.session_state[state_key] = "choosing_date"
                st.rerun()
        with col2:
            if st.button(t("no"), key=f"appt_no_{turn_no}",
                         use_container_width=True):
                st.session_state[state_key] = "declined"
                st.rerun()

    # 状态 2: 选日期（白底 + 5px 靛蓝粗条 + 强阴影）
    elif current == "choosing_date":
        st.markdown(
            f'<div style="margin-top:1.3rem;margin-bottom:0.6rem;'
            f'padding:1.2rem 1.4rem;'
            f'background:#ffffff;'
            f'border:1px solid #cbd5e1;'
            f'border-left:5px solid #4f46e5;'
            f'border-radius:12px;'
            f'box-shadow:0 8px 24px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04);">'
            f'<div style="display:flex;align-items:center;gap:0.7rem;">'
            f'<span style="font-size:1.4rem;">📅</span>'
            f'<span style="font-size:1.05rem;font-weight:800;color:#0a0a0a;'
            f'letter-spacing:-0.2px;">'
            f'{t("choose_date")}</span></div></div>',
            unsafe_allow_html=True,
        )
        dates = r.get("available_dates", [])
        cols = st.columns(4)
        for i, d in enumerate(dates):
            from datetime import datetime, timezone, timedelta
            dt = datetime.fromisoformat(d + "T00:00:00+00:00")
            local = dt.astimezone(timezone(timedelta(hours=8)))
            lang = st.session_state["lang"]
            if lang == "en":
                local_label = local.strftime("%b %d, %Y")
            elif lang == "zh-Hant":
                weekday = ["一", "二", "三", "四", "五", "六", "日"][local.weekday()]
                local_label = local.strftime(f"%m月%d日 週{weekday}")
            else:
                weekday = ["一", "二", "三", "四", "五", "六", "日"][local.weekday()]
                local_label = local.strftime(f"%m月%d日 星期{weekday}")
            with cols[i % 4]:
                if st.button(local_label, key=f"appt_date_{turn_no}_{i}",
                             use_container_width=True):
                    st.session_state[date_key] = d
                    st.session_state[state_key] = "choosing_time"
                    st.rerun()
        if st.button(t("cancel"), key=f"appt_cancel_date_{turn_no}"):
            st.session_state[state_key] = "declined"
            st.rerun()

    # 状态 3: 选时段（白底 + 5px 靛蓝粗条 + 强阴影）
    elif current == "choosing_time":
        st.markdown(
            f'<div style="margin-top:1.3rem;margin-bottom:0.6rem;'
            f'padding:1.2rem 1.4rem;'
            f'background:#ffffff;'
            f'border:1px solid #cbd5e1;'
            f'border-left:5px solid #4f46e5;'
            f'border-radius:12px;'
            f'box-shadow:0 8px 24px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04);">'
            f'<div style="display:flex;align-items:center;gap:0.7rem;">'
            f'<span style="font-size:1.4rem;">⏰</span>'
            f'<span style="font-size:1.05rem;font-weight:800;color:#0a0a0a;'
            f'letter-spacing:-0.2px;">'
            f'{t("choose_time")}</span></div></div>',
            unsafe_allow_html=True,
        )
        slots = r.get("time_slots", [])
        cols = st.columns(3)
        for i, slot in enumerate(slots):
            with cols[i % 3]:
                if st.button(slot, key=f"appt_time_{turn_no}_{i}",
                             use_container_width=True):
                    st.session_state[time_key] = slot
                    st.session_state[state_key] = "confirming"
                    st.rerun()
        if st.button(t("cancel"), key=f"appt_cancel_time_{turn_no}"):
            st.session_state[state_key] = "declined"
            st.rerun()

    # 状态 4: 确认中
    elif current == "confirming":
        selected_date = st.session_state.get(date_key, "")
        selected_time = st.session_state.get(time_key, "")
        with st.spinner(t("confirming")):
            if on_confirm_appointment:
                confirmed = on_confirm_appointment(
                    r["session_id"],
                    r.get("appointment_reason", ""),
                    selected_date,
                    selected_time,
                    st.session_state["lang"],
                )
            else:
                confirmed = {"scheduled": False}
        if confirmed and confirmed.get("scheduled"):
            st.session_state[result_key] = confirmed
            st.session_state[state_key] = "confirmed"
        else:
            st.session_state[state_key] = "failed"
        st.rerun()

    # 状态 5: 成功（白底 + 绿左边条 + 阴影）
    elif current == "confirmed":
        confirmed = st.session_state.get(result_key, {})
        local_time = format_local_time(
            confirmed.get("slot_utc", ""), st.session_state["lang"]
        )
        st.markdown(
            f'<div style="margin-top:1.3rem;margin-bottom:0.6rem;'
            f'padding:1.2rem 1.4rem;'
            f'background:#ffffff;'
            f'border:1px solid #d1fae5;'
            f'border-left:5px solid #10b981;'
            f'border-radius:12px;'
            f'box-shadow:0 8px 24px rgba(16,185,129,0.08), 0 2px 6px rgba(0,0,0,0.04);">'
            f'<div style="display:flex;align-items:center;gap:0.7rem;'
            f'margin-bottom:0.4rem;">'
            f'<span style="font-size:1.4rem;">✅</span>'
            f'<span style="font-size:1.05rem;font-weight:800;color:#065f46;">'
            f'{t("appointment_confirmed")}</span></div>'
            f'<div style="font-size:0.88rem;color:#52525b;'
            f'font-family:SF Mono,Menlo,monospace;padding-left:2.1rem;">'
            f'{t("appointment_scheduled_at")}: {local_time}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # 状态 6: 用户拒绝
    elif current == "declined":
        st.markdown(
            f'<div style="margin-top:1rem;padding:0.75rem 1.1rem;'
            f'background:#fafafa;border:1px solid #e5e7eb;'
            f'border-radius:10px;font-size:0.86rem;color:#71717a;">'
            f'{t("appointment_declined")}</div>',
            unsafe_allow_html=True,
        )

    # 状态 7: 失败
    elif current == "failed":
        st.error(t("appointment_failed"))
        if st.button(t("retry"), key=f"appt_retry_{turn_no}"):
            st.session_state[state_key] = "choosing_date"
            st.rerun()