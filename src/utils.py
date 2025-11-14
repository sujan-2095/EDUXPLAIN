"""Utility helpers for prompt building, validation, and parsing."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List

NUMERIC_FIELDS = [
    "attendance_pct",
    "avg_quiz_score",
    "avg_assignment_score",
    "class_participation_score",
    "prior_topic_score",
    "hours_studied_per_week",
]

PROMPT_TEMPLATE = """
SYSTEM: You are EduXplain, an educational analyst. Respond ONLY with minified JSON.

USER:
Given the student's numeric features, return STRICT JSON with:
  prediction: "AtRisk" or "NotAtRisk"
  probability: float 0-1
  reasons: array of exactly 3 short feature-grounded strings
  recommendation: 1-2 sentence guidance
  recommendation_ta: Tamil translation of recommendation (optional)
  recommendation_hi: Hindi translation of recommendation (optional)
  counterfactual_example: {{"change": string, "new_probability": float 0-1}}

Also include feature_weights: top 3 feature => rationale pairs, e.g.
  feature_weights: [
    {{"feature": "attendance_pct", "impact": "low attendance increases risk"}},
    ...
  ]

FEATURES:
attendance_pct: {attendance_pct}
avg_quiz_score: {avg_quiz_score}
avg_assignment_score: {avg_assignment_score}
class_participation_score: {class_participation_score}
prior_topic_score: {prior_topic_score}
hours_studied_per_week: {hours_studied_per_week}
""".strip()


@dataclass
class StudentFeatures:
    attendance_pct: float
    avg_quiz_score: float
    avg_assignment_score: float
    class_participation_score: float
    prior_topic_score: float
    hours_studied_per_week: float

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "StudentFeatures":
        def coerce(name: str) -> float:
            value = payload.get(name)
            if value is None or value == "":
                raise ValueError(f"Missing value for {name}")
            try:
                return float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid numeric value for {name}") from exc

        return cls(**{field: coerce(field) for field in NUMERIC_FIELDS})

    def to_prompt_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_prompt(features: StudentFeatures) -> str:
    return PROMPT_TEMPLATE.format(**features.to_prompt_dict())


def extract_first_json_block(text: str) -> Dict[str, Any]:
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError("Gemini response did not contain JSON")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError("Gemini JSON malformed") from exc


REQUIRED_FIELDS = {
    "prediction": str,
    "probability": (int, float),
    "reasons": list,
    "recommendation": str,
    "counterfactual_example": dict,
}


def validate_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    for field, field_type in REQUIRED_FIELDS.items():
        if field not in payload:
            raise ValueError(f"Missing field '{field}' in Gemini response")
        if not isinstance(payload[field], field_type):
            raise ValueError(f"Field '{field}' has wrong type")

    probability = float(payload["probability"])
    if probability < 0 or probability > 1:
        raise ValueError("Probability must be between 0 and 1")

    counterfactual = payload["counterfactual_example"]
    if "change" not in counterfactual or "new_probability" not in counterfactual:
        raise ValueError("Counterfactual missing keys")

    new_prob = float(counterfactual["new_probability"])
    if not 0 <= new_prob <= 1:
        raise ValueError("Counterfactual probability out of range")

    reasons = payload["reasons"]
    if not isinstance(reasons, list) or len(reasons) == 0:
        raise ValueError("Reasons must be a non-empty list")

    payload["probability"] = probability
    counterfactual["new_probability"] = new_prob
    return payload
