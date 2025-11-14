"""Simple alert logic placeholder."""
from __future__ import annotations

from typing import Dict, Optional

ALERT_THRESHOLD = 0.7


def should_alert(probability: float) -> bool:
    return probability >= ALERT_THRESHOLD


def build_alert_payload(student_features: Dict[str, float], result: Dict[str, object]) -> Dict[str, object]:
    return {
        "message": f"Student risk probability is {result['probability']:.2f}",
        "prediction": result.get("prediction"),
        "features": student_features,
        "counterfactual": result.get("counterfactual_example"),
    }
