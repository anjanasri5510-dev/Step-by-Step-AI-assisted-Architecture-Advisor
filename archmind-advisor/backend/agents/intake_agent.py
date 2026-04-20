"""Intake agent: turns a free-form project description into structured JSON."""

from __future__ import annotations

import json
import re
from typing import Any

from backend.utils.llm_client import call_llm

SYSTEM_PROMPT = """You are the Intake Agent for ArchMind, an AI architecture advisor.
Extract the key attributes from the user's project description and respond with
ONLY a single JSON object (no prose, no markdown fences) using EXACTLY this schema:

{
  "project_type": "",
  "team_size": "small/medium/large",
  "scale_requirement": "low/medium/high",
  "budget_sensitivity": "low/medium/high",
  "existing_stack": [],
  "key_constraints": []
}

Rules:
- "team_size" must be one of: "small", "medium", "large".
- "scale_requirement" must be one of: "low", "medium", "high".
- "budget_sensitivity" must be one of: "low", "medium", "high".
- "existing_stack" and "key_constraints" must be arrays of short strings.
- If a field is not stated, make a reasonable inference from context.
- Output JSON only. Do not include any text before or after the JSON object.
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
        raise ValueError(f"Intake agent response was not valid JSON: {text!r}")
    return json.loads(match.group(0))


def run_intake_agent(description: str) -> dict[str, Any]:
    """Run the intake agent on a plain-text project description.

    Args:
        description: Free-form description of the project.

    Returns:
        A dict matching the intake schema.
    """
    if not description or not description.strip():
        raise ValueError("Project description must not be empty.")

    response = call_llm(SYSTEM_PROMPT, description.strip())
    return _extract_json(response)
