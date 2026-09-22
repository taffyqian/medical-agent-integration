"""UI 组件：侧边栏、进度条、结果卡片"""
import streamlit as st

from ui_texts import QUICK_SYMPTOMS, display_drug_name
from ui_helpers import format_local_time, format_fda_warnings


def render_sidebar(t):
    with st.sidebar:
        lang_options = {"zh-Hans": "简体中文", "zh-Hant": "繁體中文", "en": "English"}
        selected_lang = st.radio(
            "🌐 " + t("lang_label"),
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
            f'<div class="card" style="padding:0.8rem 1rem;">'
            f'<div class="label">{t("session_id")}</div>'
            f'<div class="value" style="font-family:SF Mono,Menlo,monospace;'
            f'font-size:0.85rem;word-break:break-all;">'
            f'{st.session_state.session_id}</div>'
            f'</div>'
        )
        st.markdown(session_html, unsafe_allow_html=True)

        if st.button("🔄 " + t("new_session"), use_container_width=True):
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
                f'<div style="margin-top:0.6rem;">'
                f'<div class="label">{t("severity")}</div>'
                f'<span class="badge {badge_cls}">{state.get("severity", "-")}</span>'
                f'</div>'
                f'<div style="margin-top:0.6rem;">'
                f'<div class="label">{t("workflow_stage")}</div>'
                f'<span class="badge badge-info">{state.get("workflow_stage", "-")}</span>'
                f'</div>'
            )
            st.markdown(status_html, unsafe_allow_html=True)
        else:
            st.caption(t("no_state"))


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

    html = '<div class="card" style="padding:0.8rem 1.2rem;">'
    html += f'<div class="label">{t("progress_heading")}</div>'
    for idx_stage, stage in enumerate(stage_order):
        label = stage_labels[stage]
        if idx_stage < idx_current:
            cls, icon = "done", "✅"
        elif idx_stage == idx_current:
            cls, icon = "running", "⏳"
        else:
            cls, icon = "waiting", "⬜"
        html += f'<div class="progress-step {cls}">'
        html += f'<div class="progress-step-icon">{icon}</div>'
        html += f'<div>{label}</div>'
        html += '</div>'
    html += "</div>"
    placeholder.markdown(html, unsafe_allow_html=True)


def render_result_turn(t, r, turn_input, turn_no):
    with st.expander(
        f"{t('turn', n=turn_no)}  ·  {', '.join(turn_input)}",
        expanded=(turn_no == len(st.session_state.get("history", []))),
    ):
        # =========================================================
        # 紧急分支
        # =========================================================
        if r["action"] == "emergency_escalation":
            lang = st.session_state["lang"]
            if lang == "zh-Hant":
                hotline = "119（台灣）· 999（香港）· 120（中國內地）"
            elif lang == "en":
                hotline = "911 (US) · 999 (UK) · 120 (China)"
            else:
                hotline = "120（中国内地）· 119（台湾）· 999（香港）"

            matched_str = " · ".join(r.get("matched", []))

            emergency_html = (
                f'<div style="background:#ffffff;border:1px solid #fecaca;'
                f'border-left:3px solid #dc2626;border-radius:12px;'
                f'padding:1.2rem 1.4rem;margin-top:0.4rem;">'
                f'<div style="display:inline-block;background:#fee2e2;'
                f'color:#b91c1c;font-size:0.72rem;font-weight:700;'
                f'letter-spacing:1.2px;padding:0.3rem 0.7rem;'
                f'border-radius:6px;text-transform:uppercase;">'
                f'{t("emergency")}</div>'
                f'<div style="margin-top:0.9rem;font-size:1rem;'
                f'color:#1e293b;line-height:1.55;">'
                f'{t("emergency_msg")}</div>'
                f'<div style="margin-top:1rem;background:#fef2f2;'
                f'border-radius:10px;padding:0.9rem 1.2rem;'
                f'display:flex;align-items:center;justify-content:center;'
                f'gap:0.5rem;">'
                f'<span style="font-size:1.1rem;">📞</span>'
                f'<span style="font-size:1.05rem;font-weight:700;'
                f'color:#b91c1c;letter-spacing:0.3px;">{hotline}</span>'
                f'</div>'
                f'<div style="margin-top:1.1rem;display:grid;'
                f'grid-template-columns:110px 1fr;gap:0.5rem 1rem;'
                f'font-size:0.88rem;">'
                f'<div style="color:#94a3b8;font-weight:600;'
                f'text-transform:uppercase;font-size:0.72rem;'
                f'letter-spacing:0.6px;padding-top:0.15rem;">'
                f'{t("matched")}</div>'
                f'<div style="color:#1e293b;">{matched_str}</div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(emergency_html, unsafe_allow_html=True)

        # =========================================================
        # 非紧急分支
        # =========================================================
        else:
            sev = r.get("severity", "-")
            normal_html = (
                f'<div class="card" style="border-left:4px solid #22c55e;">'
                f'<span class="badge badge-normal">✅ {t("non_emergency")}</span>'
                f'<span style="margin-left:0.5rem;">'
                f'<span class="label" style="display:inline;">'
                f'{t("severity")}:</span>'
                f'<span class="value" style="display:inline;">{sev}</span>'
                f'</span></div>'
            )
            st.markdown(normal_html, unsafe_allow_html=True)

            # ---- 可能的原因 ----
            possible_causes = r.get("possible_causes", [])
            if possible_causes:
                likelihood_label = {
                    "common": t("cause_common"),
                    "possible": t("cause_possible"),
                    "less common": t("cause_less_common"),
                }
                likelihood_color = {
                    "common": "#0e7490",
                    "possible": "#0d9488",
                    "less common": "#64748b",
                }
                cause_rows = ""
                for c in possible_causes:
                    condition = c.get("condition", "")
                    likelihood = c.get("likelihood", "possible")
                    note = c.get("note", "")
                    color = likelihood_color.get(likelihood, "#64748b")
                    lbl = likelihood_label.get(likelihood, likelihood)
                    if condition:
                        cause_rows += (
                            f'<div style="display:flex;gap:0.8rem;'
                            f'align-items:flex-start;padding:0.5rem 0.9rem;'
                            f'margin-bottom:0.35rem;background:#f8fafc;'
                            f'border-left:3px solid {color};border-radius:6px;">'
                            f'<div style="flex-shrink:0;min-width:58px;'
                            f'font-size:0.72rem;font-weight:700;color:{color};'
                            f'padding-top:0.15rem;">{lbl}</div>'
                            f'<div style="font-size:0.88rem;color:#0f172a;'
                            f'line-height:1.5;">'
                            f'<strong>{condition}</strong>'
                            + (f' <span style="color:#64748b;">— {note}</span>' if note else "") +
                            f'</div></div>'
                        )

                cause_html = (
                    '<div style="background:#ffffff;'
                    'border:1px solid #cbd5e1;border-radius:10px;'
                    'padding:0;margin-top:0.6rem;overflow:hidden;">'
                    '<div style="background:#f1f5f9;padding:0.5rem 1rem;'
                    'display:flex;align-items:center;gap:0.5rem;">'
                    '<span style="font-size:0.95rem;">🔍</span>'
                    '<span style="font-size:0.82rem;font-weight:800;'
                    'color:#334155;letter-spacing:0.8px;'
                    'text-transform:uppercase;">'
                    + t("possible_causes") +
                    '</span></div>'
                    '<div style="padding:0.7rem 0.8rem;">'
                    + cause_rows +
                    '</div>'
                    '<div style="padding:0.5rem 1rem;background:#fffbeb;'
                    'border-top:1px solid #fef3c7;font-size:0.78rem;'
                    'color:#92400e;">⚠️ ' + t("cause_disclaimer") +
                    '</div></div>'
                )
                st.markdown(cause_html, unsafe_allow_html=True)

            # ---- 推荐药品 ----
            recs = r.get("recommendations", [])
            if recs:
                # 卡片式标题（浅灰底 + 左青条 + 图标）
                st.markdown(
                    f'<div style="'
                    f'background:#f1f5f9;'
                    f'border-left:3px solid #0e7490;'
                    f'border-radius:8px;'
                    f'padding:0.55rem 1rem;'
                    f'margin-top:1.2rem;'
                    f'margin-bottom:0.6rem;'
                    f'display:flex;align-items:center;gap:0.5rem;'
                    f'">'
                    f'<span style="font-size:0.95rem;">💊</span>'
                    f'<span style="font-size:0.85rem;font-weight:800;'
                    f'color:#0e7490;letter-spacing:0.6px;'
                    f'text-transform:uppercase;">'
                    f'{t("drugs")}'
                    f'</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                # 收集追问（供 app.py 底部显示）
                all_questions = []

                for rec in recs:
                    info = rec.get("drug_info", {})
                    brand = info.get("brand_name", "-") if info.get("ok") else "-"
                    for_syms = ", ".join(rec.get("symptoms", []))
                    display_name = display_drug_name(
                        rec["drug_name"], st.session_state["lang"]
                    )

                    # --- 药品卡 ---
                    drug_html = (
                        f'<div class="drug-card">'
                        f'<div class="drug-name">💊 {display_name}</div>'
                        f'<div class="drug-for">{t("for_symptoms")}: {for_syms}</div>'
                        f'<div class="drug-for">{t("brand")}: {brand}</div>'
                        f'</div>'
                    )
                    st.markdown(drug_html, unsafe_allow_html=True)

                    # --- 医疗建议 ---
                    advice_rows = []
                    if rec.get("usage_advice"):
                        advice_rows.append((t("usage_advice"), rec["usage_advice"], "#0e7490", "#f0fdfa"))
                    if rec.get("self_care"):
                        advice_rows.append((t("self_care"), rec["self_care"], "#0d9488", "#f0fdfa"))
                    if rec.get("when_to_seek_help"):
                        advice_rows.append((t("when_to_seek_help"), rec["when_to_seek_help"], "#b91c1c", "#fef2f2"))

                    if advice_rows:
                        rows_html = ""
                        for i, (label, text, color, bg) in enumerate(advice_rows):
                            is_last = (i == len(advice_rows) - 1)
                            margin = "" if is_last else "margin-bottom:0.4rem;"
                            rows_html += (
                                f'<div style="display:flex;gap:0.8rem;'
                                f'align-items:flex-start;background:{bg};'
                                f'border-left:3px solid {color};border-radius:6px;'
                                f'padding:0.55rem 0.9rem;{margin}">'
                                f'<div style="flex-shrink:0;min-width:70px;'
                                f'font-size:0.82rem;font-weight:700;color:{color};'
                                f'letter-spacing:0.2px;line-height:1.5;">{label}</div>'
                                f'<div style="font-size:0.88rem;color:#0f172a;'
                                f'line-height:1.5;">{text}</div>'
                                f'</div>'
                            )
                        advice_html = (
                            '<div style="background:#ffffff;'
                            'border:1px solid #99f6e4;border-radius:10px;'
                            'padding:0;margin-top:0.6rem;overflow:hidden;">'
                            '<div style="background:linear-gradient(90deg,#0e7490,#14b8a6);'
                            'padding:0.5rem 1rem;display:flex;align-items:center;gap:0.5rem;">'
                            '<span style="font-size:0.95rem;">💡</span>'
                            '<span style="font-size:0.82rem;font-weight:800;'
                            'color:#ffffff;letter-spacing:0.8px;'
                            'text-transform:uppercase;">'
                            + t("medical_guidance") +
                            '</span></div>'
                            '<div style="padding:0.7rem 0.8rem;">'
                            + rows_html +
                            '</div></div>'
                        )
                        st.markdown(advice_html, unsafe_allow_html=True)

                    # --- 收集追问 ---
                    for q in rec.get("followup_questions", []):
                        if q and q not in all_questions:
                            all_questions.append(q)

                    # --- FDA 警告折叠 ---
                    if info.get("ok") and info.get("warnings"):
                        with st.expander(f"📄 {t('view_warnings')}"):
                            formatted = format_fda_warnings(
                                info["warnings"], st.session_state["lang"]
                            )
                            st.markdown(
                                f'<div class="fda-content">{formatted}</div>',
                                unsafe_allow_html=True,
                            )
                    elif not info.get("ok"):
                        st.caption(t("no_fda"))

                # 把追问存到 result
                if all_questions:
                    r["_followup_questions"] = all_questions

            # ---- 预约 ----
            appt = r.get("appointment", {})
            if appt.get("scheduled"):
                local_time = format_local_time(
                    appt.get("slot_utc", ""), st.session_state["lang"]
                )
                appt_html = (
                    f'<div class="card" style="border-left:4px solid #0ea5e9;'
                    f'padding:0.75rem 1rem;">'
                    f'<div class="label">📅 {t("appointment")}</div>'
                    f'<div class="value" style="font-family:SF Mono,Menlo,monospace;">'
                    f'{local_time}</div>'
                    f'</div>'
                )
                st.markdown(appt_html, unsafe_allow_html=True)

        # ---- 事件流 ----
        with st.expander(f"🔍 {t('event_log')}"):
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