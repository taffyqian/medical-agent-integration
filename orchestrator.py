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


def analyze_symptoms(symptoms: List[str]) -> Dict:
    return _call_function("analyze_symptoms", {"symptoms_list": symptoms})


def drug_lookup(drug_name: str) -> Dict:
    return _call_function("drug_lookup", {"drug_name": drug_name})


def schedule_appointment(patient_name: str, reason: str, when: Optional[str] = None) -> Dict:
    payload: Dict[str, Any] = {"patient_name": patient_name, "reason": reason}
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
) -> Dict:
    state = load_session(session_id)

    if patient_name:
        state["patient_name"] = patient_name

    # --- Step 0: 记录原始输入（审计用）---
    state["events"].append({
        "stage": "input_received",
        "at": _now_iso(),
        "symptoms": symptoms,
    })

    # --- Step 1: 紧急检测（用原始输入，因为关键词可能出现在整句中）---
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
            "disclaimer": {
                "zh": "这是一般性信息，不能替代专业医疗建议。如有医疗问题，请联系医疗保健提供者。",
                "en": "This is general information and does not replace professional medical advice. For medical concerns, contact a healthcare provider.",
            },
            "state": state,
        }

    # --- Step 2: 症状分析（AI 返回标准化症状）---
    if progress_callback:
        progress_callback("symptom_analysis")
    analysis = analyze_symptoms(symptoms)
    state["severity"] = analysis.get("assessed_severity")
    possible_causes = analysis.get("possible_causes", [])
    ai_disclaimer = analysis.get("disclaimer", "")

    # 用 AI 返回的标准化症状更新 symptoms_history
    ai_normalized = []
    for rec in analysis.get("recommendations", []):
        sym = rec.get("symptom")
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
        enriched.append({
            "symptoms": [rec.get("symptom")] if rec.get("symptom") else [],
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
        "disclaimer": {
            "zh": "这是一般性信息，不能替代专业医疗建议。如有医疗问题，请联系医疗保健提供者。",
            "en": "This is general information and does not replace professional medical advice. For medical concerns, contact a healthcare provider.",
        },
        "ai_disclaimer": ai_disclaimer,
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