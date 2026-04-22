"""Planning agent: produces a phased execution plan for the winning pattern."""

from __future__ import annotations

import json
import re
from typing import Any

from backend.utils.llm_client import call_llm

SYSTEM_PROMPT = """You are the Planning Agent for ArchMind, an AI architecture advisor.
Given the winning architecture pattern (and any supporting context), produce a
step-by-step execution plan broken into phases.

Respond with ONLY a single JSON object (no prose, no markdown fences) using
EXACTLY this schema:

{
  "phases": [
    {
      "phase_number": 1,
      "phase_name": "",
      "duration": "",
      "steps": [],
      "deliverables": [],
      "dependencies": []
    }
  ],
  "total_duration": "",
  "team_size_needed": "",
  "tech_stack": []
}

Rules:
- "phases" must be ordered by "phase_number" starting at 1.
- "duration" and "total_duration" are short human-readable strings
  (e.g., "2 weeks", "3 months").
- "steps", "deliverables", "dependencies", and "tech_stack" must be arrays of
  short strings.
- "dependencies" may reference earlier phase names or external prerequisites;
  use an empty array if there are none.
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
            f"Planning agent response was not valid JSON: {text!r}"
        )
    return json.loads(match.group(0))


def run_planning_agent(winner: dict[str, Any]) -> dict[str, Any]:
    """Run the planning agent on the winning pattern.

    Args:
        winner: Dict describing the winning pattern. Typically includes
            pattern_name and winner_reason from the decision matrix agent, and
            may be augmented with the original recommendation details.

    Returns:
        A dict matching the planning schema.
    """
    if not isinstance(winner, dict) or not winner:
        raise ValueError("Winner input must be a non-empty JSON object.")

    user_prompt = json.dumps(winner, indent=2)
    response = call_llm(SYSTEM_PROMPT, user_prompt)
    return _extract_json(response)
