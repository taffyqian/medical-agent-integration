"""
阶段 2：给已有的 Foundry Agent 挂上四个 Function Tools
"""
import os
import requests
from typing import Dict, List, Optional

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FunctionTool, ToolSet
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

PROJECT_ENDPOINT = "https://oai-service-dev-001.services.ai.azure.com/api/projects/oai-service-dev-001-project"
AGENT_NAME = "MedicalInformationAssistant-Agent-01"

FUNCTION_BASE = os.environ["FUNCTION_BASE"]
FUNCTION_KEY = os.environ["FUNCTION_APP_KEY"]


# ---------------------------------------------------------------------------
# 调 Function App
# ---------------------------------------------------------------------------

def _post_json(path: str, payload: Dict) -> Dict:
    headers = {
        "Content-Type": "application/json",
        "x-functions-key": FUNCTION_KEY,
    }
    url = f"{FUNCTION_BASE}/{path}"
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        return {"ok": False, "message": "Non-JSON response.", "raw": resp.text}


# ---------------------------------------------------------------------------
# 四个 Function Tools
# ---------------------------------------------------------------------------

def analyze_symptoms(symptoms_list: List[str]) -> Dict:
    """Analyze a list of medical symptoms and classify severity.

    Args:
        symptoms_list: A list of symptom strings, e.g. ["headache", "fever"].

    Returns:
        A JSON-style dictionary with assessed severity and recommendations.
    """
    return _post_json("analyze_symptoms", {"symptoms_list": symptoms_list})


def drug_lookup(drug_name: str) -> Dict:
    """Look up FDA drug label information (brand name, purpose, warnings).

    Args:
        drug_name: The medication name, such as "Ibuprofen" or "aspirin".

    Returns:
        A JSON-style dictionary with brand_name, purpose, warnings.
    """
    return _post_json("drug_lookup", {"drug_name": drug_name})


def schedule_appointment(
    patient_name: str,
    reason: str,
    when: Optional[str] = None,
) -> Dict:
    """Schedule a patient appointment.

    Args:
        patient_name: Full patient name.
        reason: Reason for the visit (e.g. the symptom summary).
        when: Optional requested date/time string.

    Returns:
        A JSON-style dictionary with scheduled time.
    """
    payload: Dict = {"patient_name": patient_name, "reason": reason}
    if when:
        payload["when"] = when
    return _post_json("schedule_appointment", payload)


def emergency_escalator(symptoms: List[str]) -> Dict:
    """Assess whether symptoms require urgent or emergency escalation.

    Args:
        symptoms: A list of symptom strings, e.g. ["chest pain"].

    Returns:
        A JSON-style dictionary with is_emergency flag and guidance.
    """
    return _post_json("emergency_escalator", {"symptoms": symptoms})


# ---------------------------------------------------------------------------
# 找到已有 agent + 挂 tools
# ---------------------------------------------------------------------------

def find_agent_by_name(client: AIProjectClient, name: str):
    for a in client.agents.list_agents():
        if a.name == name:
            return a
    return None


def main():
    print(f"Connecting to: {PROJECT_ENDPOINT}")
    client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )

    existing = find_agent_by_name(client, AGENT_NAME)
    if not existing:
        raise ValueError(f"Agent not found: {AGENT_NAME}")

    print(f"Found agent: {existing.name}")
    print(f"  id:    {existing.id}")
    print(f"  model: {existing.model}")

    # 装配 4 个 tools
    user_functions = {
        analyze_symptoms,
        drug_lookup,
        schedule_appointment,
        emergency_escalator,
    }
    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)

    # 让 SDK 自动处理 agent 的 function call
    client.agents.enable_auto_function_calls(toolset)

    # 更新已有 agent（追加 tools，保留原 instructions 和 model）
    updated = client.agents.update_agent(
        agent_id=existing.id,
        toolset=toolset,
    )

    print("\n=== Agent updated ===")
    print(f"name:  {updated.name}")
    print(f"id:    {updated.id}")
    print(f"model: {updated.model}")
    print(f"tools: {[t.type for t in updated.tools]}")


if __name__ == "__main__":
    main()