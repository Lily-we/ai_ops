import json
import re
from typing import Any, Dict, Tuple

from .nova_client import NovaClient, NovaClientError


REQUIRED_TOP_KEYS = {"priorities", "tasks", "blockers", "weekly_report", "questions", "meta"}


def _safe_fallback(message: str, received_chars: int) -> Dict[str, Any]:
    return {
        "priorities": [],
        "tasks": [],
        "blockers": [],
        "weekly_report": {"done": [], "next": [], "risks": [], "asks": []},
        "questions": [{"question": message, "why": "Model output invalid or timed out."}],
        "meta": {"received_chars": received_chars, "mode": "fallback"},
    }


def _extract_json_candidate(text: str) -> str:
    """
    Try to pull a JSON object from a model response even if it adds commentary.
    """
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return text
    # Grab largest {...} block
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    return m.group(0) if m else text


def _validate_shape(obj: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(obj, dict):
        return False, "Root is not an object."
    missing = REQUIRED_TOP_KEYS - set(obj.keys())
    if missing:
        return False, f"Missing keys: {sorted(missing)}"
    # Light type checks
    if not isinstance(obj["tasks"], list):
        return False, "tasks must be a list"
    if not isinstance(obj["blockers"], list):
        return False, "blockers must be a list"
    if not isinstance(obj["priorities"], list):
        return False, "priorities must be a list"
    if not isinstance(obj["questions"], list):
        return False, "questions must be a list"
    if not isinstance(obj["weekly_report"], dict):
        return False, "weekly_report must be an object"
    if not isinstance(obj["meta"], dict):
        return False, "meta must be an object"
    return True, "ok"


SYSTEM_PROMPT = """
You are an information extraction engine for small-team ops notes.

Return ONLY valid JSON. No markdown, no backticks, no commentary.
Do NOT invent owners or due dates. If not explicitly stated, use null (for due) and "unassigned" (for owner).
Ignore social chatter that is not actionable.
Use lowercase enums: urgency in {"high","medium","low"} and status in {"todo","doing","done","blocked"}.
If notes are too vague, add clarifying questions in questions[].
"""


def build_user_prompt(notes_text: str) -> str:
    # Keep it explicit: exact schema contract for frontend
    return f"""
Extract structured ops data from the notes below and output JSON EXACTLY with this schema:

{{
  "priorities": [{{"title": str, "reason": str, "urgency": "high"|"medium"|"low"}}],
  "tasks": [{{"title": str, "owner": str, "due": str|null, "status": "todo"|"doing"|"done"|"blocked", "confidence": float}}],
  "blockers": [{{"title": str, "impacts": [str], "suggested_fix": str, "severity": "low"|"medium"|"high"}}],
  "weekly_report": {{"done": [str], "next": [str], "risks": [str], "asks": [str]}},
  "questions": [{{"question": str, "why": str}}],
  "meta": {{"received_chars": int, "mode": "nova"}}
}}

NOTES:
\"\"\"{notes_text}\"\"\"
"""


def extract_ops(notes_text: str, client: NovaClient) -> Dict[str, Any]:
    received_chars = len(notes_text)

    user_prompt = build_user_prompt(notes_text)

    try:
        raw = client.invoke_text(system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt)
        candidate = _extract_json_candidate(raw)
        obj = json.loads(candidate)

        ok, why = _validate_shape(obj)
        if ok:
            obj["meta"]["received_chars"] = received_chars
            obj["meta"]["mode"] = "nova"
            return obj

        # One retry: ask Nova to repair into valid JSON only
        repair_user = f"""
Fix the following into VALID JSON ONLY that matches the schema exactly.
No commentary. Output JSON only.

BROKEN_OUTPUT:
{raw}
"""
        raw2 = client.invoke_text(system_prompt=SYSTEM_PROMPT, user_prompt=repair_user, max_tokens=900, temperature=0.0)
        candidate2 = _extract_json_candidate(raw2)
        obj2 = json.loads(candidate2)

        ok2, why2 = _validate_shape(obj2)
        if ok2:
            obj2["meta"]["received_chars"] = received_chars
            obj2["meta"]["mode"] = "nova"
            return obj2

        return _safe_fallback(f"Model output invalid after retry: {why2}", received_chars)

    except (NovaClientError, json.JSONDecodeError) as e:
        return _safe_fallback(f"Model error: {str(e)}", received_chars)
