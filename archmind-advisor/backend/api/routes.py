"""HTTP routes for the ArchMind backend."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.agents.intake_agent import run_intake_agent
from backend.agents.recommendation_agent import run_recommendation_agent

router = APIRouter()


class AnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=1)


class AnalyzeResponse(BaseModel):
    intake: dict[str, Any]
    recommendations: list[dict[str, Any]]


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run the intake agent, then the recommendation agent, and return both."""
    try:
        intake = run_intake_agent(request.description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    try:
        recommendations = run_recommendation_agent(intake)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return AnalyzeResponse(intake=intake, recommendations=recommendations)
