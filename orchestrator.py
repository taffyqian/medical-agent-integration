"""
Medical Agent Orchestrator
"""
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

FUNCTION_BASE = os.environ["FUNCTION_BASE"]
FUNCTION_KEY = os.environ["FUNCTION_APP_KEY"]
STORAGE_ACCOUNT_URL = os.environ["STORAGE_ACCOUNT_URL"]
SESSION_CONTAINER = os.environ.get("SESSION_CONTAINER", "sessions")

# =====================================================================
# 固定 disclaimer（不依赖 AI 生成）
# =====================================================================
DISCLAIMER_ZH = "以上为常见可能性参考，不构成诊断。如症状持续或加重，请咨询医生。"
DISCLAIMER_EN = ("This is for reference only, not a diagnosis. "
                 "Consult a doctor if symptoms persist or worsen.")

_blob_service = None


def _get_blob_service() -> BlobServiceClient:
    global _blob_service
    if _blob_service is None:
        conn_str = os.environ.get("SESSION_STORAGE_CONN")
        if conn_str:
            # 云端（Streamlit Cloud）走连接字符串
            _blob_service = BlobServiceClient.from_connection_string(conn_str)
        else:
            # 本地走 DefaultAzureCredential
            _blob_service = BlobServiceClient(
                account_url=STORAGE_ACCOUNT_URL,
                credential=DefaultAzureCredential(),
            )
    return _blob_service


# =====================================================================
# 调 Function App
# =====================================================================

def _call_function(path: str, payload: Dict) -> Dict:
    url = f"{FUNCTION_BASE}/{path}"
    headers = {
        "Content-Type": "application/json",
        "x-functions-key": FUNCTION_KEY,
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        return {"ok": False, "message": "Non-JSON response", "raw": resp.text}


def emergency_escalator(symptoms: List[str]) -> Dict:
    return _call_function("emergency_escalator", {"symptoms": symptoms})


def analyze_symptoms(symptoms: List[str], lang: str = "zh-Hans") -> Dict:
    return _call_function("analyze_symptoms", {
        "symptoms_list": symptoms,
        "lang": lang,
    })


def drug_lookup(drug_name: str) -> Dict:
    return _call_function("drug_lookup", {"drug_name": drug_name})


def schedule_appointment(patient_name: str, reason: str,
                          when: Optional[str] = None,
                          lang: str = "zh-Hans") -> Dict:
    payload: Dict[str, Any] = {
        "patient_name": patient_name,
        "reason": reason,
        "lang": lang,
    }
    if when:
        payload["when"] = when
    return _call_function("schedule_appointment", payload)


# =====================================================================
# 会话状态（Blob Storage）
# =====================================================================

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _session_blob_name(session_id: str) -> str:
    return f"{session_id}.json"


def load_session(session_id: str) -> Dict:
    client = _get_blob_service().get_blob_client(
        container=SESSION_CONTAINER, blob=_session_blob_name(session_id)
    )
    try:
        data = client.download_blob().readall()
        return json.loads(data)
    except Exception:
        return {
            "session_id": session_id,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "patient_name": None,
            "symptoms_history": [],
            "most_recent_symptom": None,
            "severity": None,
            "recommendations": [],
            "appointment": None,
            "workflow_stage": "new",
            "events": [],
        }


def save_session(session_id: str, state: Dict) -> None:
    state["updated_at"] = _now_iso()
    client = _get_blob_service().get_blob_client(
        container=SESSION_CONTAINER, blob=_session_blob_name(session_id)
    )
    client.upload_blob(
        json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8"),
        overwrite=True,
    )


# =====================================================================
# Orchestrator 核心
# =====================================================================

def orchestrate(
    session_id: str,
    symptoms: List[str],
    patient_name: Optional[str] = None,
    progress_callback=None,
    lang: str = "zh-Hans",
) -> Dict:
    state = load_session(session_id)

    if patient_name:
        state["patient_name"] = patient_name

    # 固定 disclaimer（按语言）
    fixed_disclaimer = DISCLAIMER_ZH if lang.startswith("zh") else DISCLAIMER_EN

    # --- Step 0: 记录原始输入（审计用）---
    state["events"].append({
        "stage": "input_received",
        "at": _now_iso(),
        "symptoms": symptoms,
        "lang": lang,
    })

    # --- Step 1: 紧急检测 ---
    if progress_callback:
        progress_callback("emergency_check")
    emerg = emergency_escalator(symptoms)
    state["events"].append({
        "stage": "emergency_check",
        "at": _now_iso(),
        "result": emerg,
    })

    if emerg.get("is_emergency"):
        # 紧急：用 emergency_escalator 返回的标准化症状
        normalized = emerg.get("normalized") or symptoms
        for s in normalized:
            if s not in state["symptoms_history"]:
                state["symptoms_history"].append(s)
        if normalized:
            state["most_recent_symptom"] = normalized[-1]

        state["severity"] = "emergency"
        state["workflow_stage"] = "escalated"
        save_session(session_id, state)
        return {
            "session_id": session_id,
            "action": "emergency_escalation",
            "message": emerg.get("message", "请立即就医。"),
            "matched": emerg.get("matched", []),
            "skipped": [
                "analyze_symptoms",
                "drug_lookup",
                "schedule_appointment",
            ],
            "disclaimer": fixed_disclaimer,
            "state": state,
        }

    # --- Step 2: 症状分析（AI 返回标准化症状）---
    if progress_callback:
        progress_callback("symptom_analysis")
    analysis = analyze_symptoms(symptoms, lang=lang)
    state["severity"] = analysis.get("assessed_severity")
    possible_causes = analysis.get("possible_causes", [])

    # 用 AI 返回的标准化症状更新 symptoms_history
    ai_normalized = []
    for rec in analysis.get("recommendations", []):
        # 兼容 "symptoms"（复数 list）和 "symptom"（单数 str）
        syms = rec.get("symptoms") or rec.get("symptom")
        if isinstance(syms, str):
            syms = [syms]
        for sym in (syms or []):
            if sym and sym not in ai_normalized:
                ai_normalized.append(sym)

    normalized_for_history = ai_normalized if ai_normalized else symptoms
    for s in normalized_for_history:
        if s not in state["symptoms_history"]:
            state["symptoms_history"].append(s)
    if normalized_for_history:
        state["most_recent_symptom"] = normalized_for_history[-1]

    state["events"].append({
        "stage": "symptom_analysis",
        "at": _now_iso(),
        "result": analysis,
        "normalized_symptoms": ai_normalized,
    })

    # --- Step 3: 药品查询 ---
    if progress_callback:
        progress_callback("drug_lookup")
    recommendations = analysis.get("recommendations", [])
    enriched = []
    for rec in recommendations:
        drug_name = rec.get("drug_name")
        if not drug_name:
            continue
        info = rec.get("drug_info") or drug_lookup(drug_name)
        # 用 "symptoms"（list）统一
        syms = rec.get("symptoms") or rec.get("symptom")
        if isinstance(syms, str):
            syms = [syms]
        enriched.append({
            "symptoms": syms or [],
            "drug_name": drug_name,
            "drug_info": info,
            "usage_advice": rec.get("usage_advice", ""),
            "self_care": rec.get("self_care", ""),
            "when_to_seek_help": rec.get("when_to_seek_help", ""),
            "followup_questions": rec.get("followup_questions", []),
        })
        state["events"].append({
            "stage": "drug_lookup",
            "at": _now_iso(),
            "drug": drug_name,
            "ok": info.get("ok", False),
        })
    state["recommendations"] = enriched

    # --- Step 4: 预约（用标准化症状名）---
    if progress_callback:
        progress_callback("appointment")
    reason = ", ".join(normalized_for_history)
    appointment = schedule_appointment(
        patient_name=state.get("patient_name") or "Unknown",
        reason=reason,
        lang=lang,
    )
    state["appointment"] = appointment
    state["events"].append({
        "stage": "appointment",
        "at": _now_iso(),
        "result": appointment,
    })

    # --- Step 5: 写回 ---
    if progress_callback:
        progress_callback("completed")
    state["workflow_stage"] = "completed"
    save_session(session_id, state)

    return {
        "session_id": session_id,
        "action": "full_workflow",
        "severity": state["severity"],
        "possible_causes": possible_causes,
        "recommendations": enriched,
        "appointment": appointment,
        # 固定 disclaimer（不用 AI 返回的）
        "disclaimer": fixed_disclaimer,
        "state": state,
    }


# =====================================================================
# CLI
# =====================================================================

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print('  python orchestrator.py --new "symptom1,symptom2" [patient_name]')
        print('  python orchestrator.py <session_id> "symptom1,symptom2" [patient_name]')
        sys.exit(1)

    args = sys.argv[1:]
    if args[0] == "--new":
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        symptoms = [s.strip() for s in args[1].split(",") if s.strip()]
        patient_name = args[2] if len(args) > 2 else None
        print(f"New session: {session_id}")
    else:
        session_id = args[0]
        symptoms = [s.strip() for s in args[1].split(",") if s.strip()]
        patient_name = args[2] if len(args) > 2 else None

    result = orchestrate(session_id, symptoms, patient_name)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()