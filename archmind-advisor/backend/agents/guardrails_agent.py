"""Guardrails agent: identifies risks and anti-patterns in the recommended architecture."""

from __future__ import annotations

import json
import re
from typing import Any

from backend.utils.llm_client import call_llm

SYSTEM_PROMPT = """You are the Guardrails Agent for ArchMind, an AI architecture advisor.
Given the full analysis JSON so far (project summary, recommendations, decision
matrix, and execution plan), identify risks, anti-patterns, and compliance
flags in the recommended architecture and suggest concrete recommendations.

Respond with ONLY a single JSON object (no prose, no markdown fences) using
EXACTLY this schema:

{
  "risk_level": "low/medium/high",
  "risks": [
    {
      "risk_name": "",
      "description": "",
      "severity": "low/medium/high",
      "mitigation": ""
    }
  ],
  "anti_patterns_detected": [],
  "compliance_flags": [],
  "recommendations": []
}

Rules:
- "risk_level" and each risk "severity" must be one of: "low", "medium", "high".
- "risks" is an array of objects with the exact keys shown above.
- "anti_patterns_detected", "compliance_flags", and "recommendations" are
  arrays of short strings.
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
            f"Guardrails agent response was not valid JSON: {text!r}"
        )
    return json.loads(match.group(0))


def run_guardrails_agent(analysis: dict[str, Any]) -> dict[str, Any]:
    """Run the guardrails agent against the full analysis so far.

    Args:
        analysis: Dict containing project summary, recommendations, decision
            matrix, and execution plan produced by earlier agents.

    Returns:
        A dict matching the guardrails schema.
    """
    if not isinstance(analysis, dict) or not analysis:
        raise ValueError("Analysis input must be a non-empty JSON object.")

    user_prompt = json.dumps(analysis, indent=2)
    response = call_llm(SYSTEM_PROMPT, user_prompt)
    return _extract_json(response)
