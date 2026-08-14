import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).with_name(".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not configured.")

if not OPENAI_MODEL:
    raise RuntimeError("OPENAI_MODEL is not configured.")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(
    title="ClarifAI API",
    description="Proof-of-concept API for patient-friendly clinical-text simplification.",
    version="0.1.0",
)

allowed_origins = ["*"] if FRONTEND_ORIGIN == "*" else [FRONTEND_ORIGIN]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


class SimplificationRequest(BaseModel):
    text: str = Field(min_length=3, max_length=20000)
    record_type: str = Field(default="clinical_note")


CLARIFAI_SCHEMA = {
    "type": "object",
    "properties": {
        "plain_language_summary": {"type": "string"},
        "medical_terms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "term": {"type": "string"},
                    "meaning": {"type": "string"},
                },
                "required": ["term", "meaning"],
                "additionalProperties": False,
            },
        },
        "medication": {
            "type": ["object", "null"],
            "properties": {
                "name": {"type": ["string", "null"]},
                "strength": {"type": ["string", "null"]},
                "dose": {"type": ["string", "null"]},
                "frequency": {"type": ["string", "null"]},
                "timing": {"type": ["string", "null"]},
                "route": {"type": ["string", "null"]},
                "duration": {"type": ["string", "null"]},
                "plain_language_instruction": {"type": ["string", "null"]},
            },
            "required": [
                "name",
                "strength",
                "dose",
                "frequency",
                "timing",
                "route",
                "duration",
                "plain_language_instruction",
            ],
            "additionalProperties": False,
        },
        "uncertainty_present": {"type": "boolean"},
        "needs_clinician_review": {"type": "boolean"},
        "warning": {"type": ["string", "null"]},
    },
    "required": [
        "plain_language_summary",
        "medical_terms",
        "medication",
        "uncertainty_present",
        "needs_clinician_review",
        "warning",
    ],
    "additionalProperties": False,
}


SYSTEM_INSTRUCTIONS = """
You are ClarifAI, a clinical-language simplification system.

Your job is NOT to diagnose, prescribe, or modify medical information.
Your only job is to translate clinical language into language that a patient can understand.

STRICT RULES:

1. Preserve the medical meaning exactly.
2. Never introduce a diagnosis that is not explicitly present.
3. Never remove uncertainty.
4. Preserve negation exactly.
5. Never change medication names, doses, units, frequencies, routes, durations, dates, or measurements.
6. When processing medication instructions, explain the EXISTING prescription only.
7. Never recommend starting, stopping, increasing, decreasing, or changing medication.
8. Expand abbreviations where possible.
9. Explain difficult medical terminology.
10. Prefer plain language and short sentences.
11. If the original text is ambiguous or cannot safely be simplified, set needs_clinician_review=true.
12. Do not give additional medical advice.
13. The original clinical record remains authoritative.

Examples of dangerous transformations that are forbidden:

"possible pneumonia" -> "you have pneumonia"
"no evidence of malignancy" -> "evidence of cancer"
"5 mg" -> "50 mg"
"BID" -> "three times daily"
"""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/simplify")
def simplify(request: SimplificationRequest):
    try:
        user_input = f"""
RECORD TYPE:
{request.record_type}

ORIGINAL RECORD:
{request.text}
"""

        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_INSTRUCTIONS,
            input=user_input,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "clarifai_simplification",
                    "strict": True,
                    "schema": CLARIFAI_SCHEMA,
                }
            },
        )

        if not response.output_text:
            raise RuntimeError("Model returned an empty response.")

        return json.loads(response.output_text)

    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Model returned invalid JSON: {exc}",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Simplification failed: {exc}",
        ) from exc
