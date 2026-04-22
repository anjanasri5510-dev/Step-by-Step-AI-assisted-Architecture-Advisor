"""Rollback agent: produces rollback strategies for the execution plan."""

from __future__ import annotations

import json
import re
from typing import Any

from backend.utils.llm_client import call_llm

SYSTEM_PROMPT = """You are the Rollback Agent for ArchMind, an AI architecture advisor.
Given the execution plan (phases) and the identified risks, produce a rollback
strategy for each phase and an overall rollback complexity rating.

Respond with ONLY a single JSON object (no prose, no markdown fences) using
EXACTLY this schema:

{
  "rollback_strategies": [
    {
      "phase_number": 1,
      "phase_name": "",
      "rollback_trigger": "",
      "rollback_steps": [],
      "recovery_time": "",
      "data_backup_required": true
    }
  ],
  "emergency_contacts": [],
  "overall_rollback_complexity": "low/medium/high"
}

Rules:
- Include one rollback strategy per phase in the execution plan, ordered by
  "phase_number" starting at 1, with "phase_name" matching the plan.
- "rollback_trigger" is a short description of the condition that would
  require a rollback for that phase.
- "rollback_steps" is an array of short strings describing the steps to take.
- "recovery_time" is a short human-readable string (e.g., "2 hours", "1 day").
- "data_backup_required" is a boolean.
- "emergency_contacts" is an array of short strings describing roles or
  contact channels (do NOT invent personal names, emails, or phone numbers).
- "overall_rollback_complexity" must be one of: "low", "medium", "high".
- Output JSON only. No commentary before or after the object.
"""


def _extract_json(text: str) -> dict[str, Any]:
    """Parse the first JSON object found in the model's response."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(
            f"Rollback agent response was not valid JSON: {text!r}"
        )
    return json.loads(match.group(0))


def run_rollback_agent(
    execution_plan: dict[str, Any],
    guardrails: dict[str, Any],
) -> dict[str, Any]:
    """Run the rollback agent on the execution plan and guardrails output.

    Args:
        execution_plan: Dict produced by the planning agent.
        guardrails: Dict produced by the guardrails agent containing risks.

    Returns:
        A dict matching the rollback schema.
    """
    if not isinstance(execution_plan, dict) or not execution_plan:
        raise ValueError("Execution plan input must be a non-empty JSON object.")
    if not isinstance(guardrails, dict) or not guardrails:
        raise ValueError("Guardrails input must be a non-empty JSON object.")

    payload = {
        "execution_plan": execution_plan,
        "risks": guardrails.get("risks", []),
        "risk_level": guardrails.get("risk_level", ""),
        "anti_patterns_detected": guardrails.get("anti_patterns_detected", []),
    }
    user_prompt = json.dumps(payload, indent=2)
    response = call_llm(SYSTEM_PROMPT, user_prompt)
    return _extract_json(response)
