"""HTTP routes for the ArchMind backend."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.agents.decision_matrix_agent import run_decision_matrix_agent
from backend.agents.guardrails_agent import run_guardrails_agent
from backend.agents.intake_agent import run_intake_agent
from backend.agents.planning_agent import run_planning_agent
from backend.agents.recommendation_agent import run_recommendation_agent
from backend.agents.rollback_agent import run_rollback_agent
from backend.utils.response_formatter import format_final_response

router = APIRouter()


class AnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=1)


def _find_winning_recommendation(
    recommendations: list[dict[str, Any]],
    winner_name: str,
) -> dict[str, Any]:
    """Return the recommendation whose pattern_name matches the winner."""
    for rec in recommendations:
        if isinstance(rec, dict) and rec.get("pattern_name") == winner_name:
            return rec
    return {}


@router.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    """Chain all 6 agents and return the combined analysis.

    Each agent is executed with its own error boundary. If any agent fails, the
    endpoint returns whatever has been produced so far along with an ``errors``
    mapping of agent name to error message.
    """
    errors: dict[str, str] = {}

    project_summary: dict[str, Any] = {}
    recommendations: list[dict[str, Any]] = []
    decision_matrix: dict[str, Any] = {}
    execution_plan: dict[str, Any] = {}
    guardrails: dict[str, Any] = {}
    rollback_strategies: dict[str, Any] = {}

    try:
        project_summary = run_intake_agent(request.description)
    except ValueError as exc:
        # Bad request from the caller - no useful partial response to return.
        raise HTTPException(
            status_code=400, detail=f"intake_agent: {exc}"
        ) from exc
    except Exception as exc:  # noqa: BLE001 - surfaced to caller
        errors["intake_agent"] = str(exc)
        return format_final_response(
            project_summary=project_summary,
            recommendations=recommendations,
            decision_matrix=decision_matrix,
            execution_plan=execution_plan,
            guardrails=guardrails,
            rollback_strategies=rollback_strategies,
            errors=errors,
        )

    try:
        recommendations = run_recommendation_agent(project_summary)
    except Exception as exc:  # noqa: BLE001
        errors["recommendation_agent"] = str(exc)
        return format_final_response(
            project_summary=project_summary,
            recommendations=recommendations,
            decision_matrix=decision_matrix,
            execution_plan=execution_plan,
            guardrails=guardrails,
            rollback_strategies=rollback_strategies,
            errors=errors,
        )

    try:
        decision_matrix = run_decision_matrix_agent(recommendations)
    except Exception as exc:  # noqa: BLE001
        errors["decision_matrix_agent"] = str(exc)
        return format_final_response(
            project_summary=project_summary,
            recommendations=recommendations,
            decision_matrix=decision_matrix,
            execution_plan=execution_plan,
            guardrails=guardrails,
            rollback_strategies=rollback_strategies,
            errors=errors,
        )

    winner_name = decision_matrix.get("winner", "")
    winner_details = _find_winning_recommendation(recommendations, winner_name)
    winner_payload: dict[str, Any] = {
        "pattern_name": winner_name,
        "winner_reason": decision_matrix.get("winner_reason", ""),
        "recommendation": winner_details,
        "project_summary": project_summary,
    }

    try:
        execution_plan = run_planning_agent(winner_payload)
    except Exception as exc:  # noqa: BLE001
        errors["planning_agent"] = str(exc)
        return format_final_response(
            project_summary=project_summary,
            recommendations=recommendations,
            decision_matrix=decision_matrix,
            execution_plan=execution_plan,
            guardrails=guardrails,
            rollback_strategies=rollback_strategies,
            errors=errors,
        )

    analysis_so_far: dict[str, Any] = {
        "project_summary": project_summary,
        "recommendations": recommendations,
        "decision_matrix": decision_matrix,
        "execution_plan": execution_plan,
    }

    try:
        guardrails = run_guardrails_agent(analysis_so_far)
    except Exception as exc:  # noqa: BLE001
        errors["guardrails_agent"] = str(exc)
        return format_final_response(
            project_summary=project_summary,
            recommendations=recommendations,
            decision_matrix=decision_matrix,
            execution_plan=execution_plan,
            guardrails=guardrails,
            rollback_strategies=rollback_strategies,
            errors=errors,
        )

    try:
        rollback_strategies = run_rollback_agent(execution_plan, guardrails)
    except Exception as exc:  # noqa: BLE001
        errors["rollback_agent"] = str(exc)

    return format_final_response(
        project_summary=project_summary,
        recommendations=recommendations,
        decision_matrix=decision_matrix,
        execution_plan=execution_plan,
        guardrails=guardrails,
        rollback_strategies=rollback_strategies,
        errors=errors or None,
    )
