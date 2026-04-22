"""Helpers for shaping the final /analyze response."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

PROJECT_NAME = "ArchMind"
VERSION = "1.0"
TOTAL_AGENTS_USED = 6


def format_final_response(
    project_summary: dict[str, Any] | None = None,
    recommendations: list[dict[str, Any]] | None = None,
    decision_matrix: dict[str, Any] | None = None,
    execution_plan: dict[str, Any] | None = None,
    guardrails: dict[str, Any] | None = None,
    rollback_strategies: dict[str, Any] | None = None,
    errors: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Combine all agent outputs into the final response payload.

    Missing outputs are normalized to empty containers so callers always get a
    consistent shape. Any per-agent errors are attached under an ``errors``
    key, and a ``metadata`` block is appended.

    Args:
        project_summary: Output from the intake agent.
        recommendations: Output from the recommendation agent.
        decision_matrix: Output from the decision matrix agent.
        execution_plan: Output from the planning agent.
        guardrails: Output from the guardrails agent.
        rollback_strategies: Output from the rollback agent.
        errors: Mapping of agent name to error message for failed agents.

    Returns:
        A dict containing the combined response plus a metadata block.
    """
    response: dict[str, Any] = {
        "project_summary": project_summary or {},
        "recommendations": recommendations or [],
        "decision_matrix": decision_matrix or {},
        "execution_plan": execution_plan or {},
        "guardrails": guardrails or {},
        "rollback_strategies": rollback_strategies or {},
    }

    if errors:
        response["errors"] = errors

    response["metadata"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_agents_used": TOTAL_AGENTS_USED,
        "project_name": PROJECT_NAME,
        "version": VERSION,
    }

    return response
