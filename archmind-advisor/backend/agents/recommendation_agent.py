"""Recommendation agent: proposes two architecture patterns based on intake data."""

from __future__ import annotations

import json
import re
from typing import Any

from backend.utils.llm_client import call_llm

SYSTEM_PROMPT = """You are the Recommendation Agent for ArchMind, an AI architecture advisor.
Given a JSON object describing a project (produced by the intake agent), recommend
EXACTLY TWO architecture patterns that best fit the project.

Respond with ONLY a JSON array (no prose, no markdown fences) of exactly two
objects using this schema:

[
  {
    "pattern_name": "",
    "why_it_fits": "",
    "trade_offs": {
      "pros": [],
      "cons": []
    },
    "best_for": ""
  },
  {
    "pattern_name": "",
    "why_it_fits": "",
    "trade_offs": {
      "pros": [],
      "cons": []
    },
    "best_for": ""
  }
]

Rules:
- Return exactly two recommendations.
- "pros" and "cons" must be arrays of short strings.
- Output JSON only. No commentary before or after the array.
"""


def _extract_json_array(text: str) -> list[dict[str, Any]]:
    """Parse the first JSON array found in the model's response."""
    text = text.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if not match:
            raise ValueError(
                f"Recommendation agent response was not valid JSON: {text!r}"
            )
        data = json.loads(match.group(0))

    if not isinstance(data, list):
        raise ValueError("Recommendation agent must return a JSON array.")
    return data


def run_recommendation_agent(
    intake: dict[str, Any],
) -> list[dict[str, Any]]:
    """Run the recommendation agent on structured intake data.

    Args:
        intake: JSON dict produced by the intake agent.

    Returns:
        A list of two recommendation dicts.
    """
    if not isinstance(intake, dict):
        raise ValueError("Intake input must be a JSON object.")

    user_prompt = json.dumps(intake, indent=2)
    response = call_llm(SYSTEM_PROMPT, user_prompt)
    return _extract_json_array(response)
