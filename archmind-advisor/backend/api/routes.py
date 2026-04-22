"""HTTP routes for the ArchMind backend."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.agents.decision_matrix_agent import run_decision_matrix_agent
from backend.agents.intake_agent import run_intake_agent
from backend.agents.planning_agent import run_planning_agent
from backend.agents.recommendation_agent import run_recommendation_agent

router = APIRouter()


class AnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=1)


class AnalyzeResponse(BaseModel):
    project_summary: dict[str, Any]
    recommendations: list[dict[str, Any]]
    decision_matrix: dict[str, Any]
    execution_plan: dict[str, Any]


def _find_winning_recommendation(
    recommendations: list[dict[str, Any]],
    winner_name: str,
) -> dict[str, Any]:
    """Return the recommendation whose pattern_name matches the winner."""
    for rec in recommendations:
        if isinstance(rec, dict) and rec.get("pattern_name") == winner_name:
            return rec
    return {}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Chain intake → recommendation → decision matrix → planning agents."""
    try:
        project_summary = run_intake_agent(request.description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"intake_agent: {exc}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"intake_agent: {exc}") from exc

    try:
        recommendations = run_recommendation_agent(project_summary)
    except ValueError as exc:
        raise HTTPException(
            status_code=502, detail=f"recommendation_agent: {exc}"
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502, detail=f"recommendation_agent: {exc}"
        ) from exc

    try:
        decision_matrix = run_decision_matrix_agent(recommendations)
    except ValueError as exc:
        raise HTTPException(
            status_code=502, detail=f"decision_matrix_agent: {exc}"
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502, detail=f"decision_matrix_agent: {exc}"
        ) from exc

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
    except ValueError as exc:
        raise HTTPException(
            status_code=502, detail=f"planning_agent: {exc}"
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502, detail=f"planning_agent: {exc}"
        ) from exc

    return AnalyzeResponse(
        project_summary=project_summary,
        recommendations=recommendations,
        decision_matrix=decision_matrix,
        execution_plan=execution_plan,
    )
