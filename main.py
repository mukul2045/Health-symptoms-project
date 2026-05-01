"""
Symptom Checker API — FastAPI + rule-based healthcare mapping.
For demos/education only; not a substitute for professional medical advice.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from symptom_mapper import parse_symptom_input, suggest_conditions

app = FastAPI(
    title="Symptom Checker API",
    description="Maps user-reported symptoms to possible conditions using weighted overlap on a curated ruleset.",
    version="1.0.0",
)


class CheckRequest(BaseModel):
    symptoms: str = Field(
        ...,
        examples=["fever, cough"],
        description="Comma-separated symptoms, e.g. 'fever, cough, fatigue'",
    )
    top_k: int = Field(5, ge=1, le=20, description="Max number of suggestions to return")


class PossibleCondition(BaseModel):
    name: str
    match_score: float = Field(..., description="Heuristic 0–1; higher = more symptom overlap")
    advice: str


class CheckResponse(BaseModel):
    input_symptoms: list[str]
    possible_conditions: list[PossibleCondition]
    disclaimer: str


DISCLAIMER = (
    "This API uses simplified rules for demonstration only. It does not diagnose disease. "
    "Always consult a qualified clinician for medical decisions."
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/check", response_model=CheckResponse)
def check_symptoms(body: CheckRequest):
    tokens = parse_symptom_input(body.symptoms)
    if not tokens:
        raise HTTPException(status_code=400, detail="Provide at least one symptom.")

    ranked = suggest_conditions(tokens, top_k=body.top_k)
    if not ranked:
        return CheckResponse(
            input_symptoms=sorted(tokens),
            possible_conditions=[],
            disclaimer=DISCLAIMER
            + " No known profile matched strongly - try more specific phrases from the docs.",
        )

    return CheckResponse(
        input_symptoms=sorted(tokens),
        possible_conditions=[
            PossibleCondition(name=c.name, match_score=round(score, 3), advice=c.advice)
            for c, score in ranked
        ],
        disclaimer=DISCLAIMER,
    )


@app.get("/check", response_model=CheckResponse)
def check_symptoms_get(
    symptoms: str = Query(..., description="Comma-separated symptoms"),
    top_k: int = Query(5, ge=1, le=20),
):
    return check_symptoms(CheckRequest(symptoms=symptoms, top_k=top_k))


@app.get("/conditions")
def list_conditions():
    """Expose supported condition names and symptom keywords for transparency."""
    from symptom_mapper import CONDITIONS

    return [
        {"name": c.name, "symptom_keywords": sorted(c.symptoms)} for c in CONDITIONS
    ]
