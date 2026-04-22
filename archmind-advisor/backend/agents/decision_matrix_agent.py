"""Decision matrix agent: compares recommended architecture patterns."""

from __future__ import annotations

import json
import re
from typing import Any

from backend.utils.llm_client import call_llm

SYSTEM_PROMPT = """You are the Decision Matrix Agent for ArchMind, an AI architecture advisor.
Given a JSON array of architecture pattern recommendations (each with
pattern_name, why_it_fits, trade_offs, best_for), produce a decision matrix
comparing the patterns and pick a winner.

Respond with ONLY a single JSON object (no prose, no markdown fences) using
EXACTLY this schema:

{
  "matrix": [
    {
      "pattern_name": "",
      "scalability": "low/medium/high",
      "complexity": "low/medium/high",
      "cost": "low/medium/high",
      "team_fit": "low/medium/high",
      "time_to_implement": "low/medium/high",
      "overall_score": 0
    }
  ],
  "winner": "",
  "winner_reason": ""
}

Rules:
- Include one matrix entry for each input pattern, preserving their order.
- "scalability", "complexity", "cost", "team_fit", and "time_to_implement"
  must each be one of: "low", "medium", "high".
- "overall_score" is an integer from 0 to 100 reflecting overall fit
  (higher is better).
- "winner" MUST be the pattern_name of the entry with the highest overall_score.
- "winner_reason" is a concise explanation (1-3 sentences).
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
            f"Decision matrix agent response was not valid JSON: {text!r}"
        )
    return json.loads(match.group(0))


def run_decision_matrix_agent(
    recommendations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run the decision matrix agent on recommendation output.

    Args:
        recommendations: List of recommendation dicts from the recommendation
            agent.

    Returns:
        A dict matching the decision matrix schema.
    """
    if not isinstance(recommendations, list) or not recommendations:
        raise ValueError(
            "Recommendations input must be a non-empty list."
        )

    user_prompt = json.dumps(recommendations, indent=2)
    response = call_llm(SYSTEM_PROMPT, user_prompt)
    return _extract_json(response)
