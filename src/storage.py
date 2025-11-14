"""Storage helpers for EduXplain using SQLAlchemy."""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from src.database import Prediction, db


def save_prediction(student_payload: Dict[str, Any], result: Dict[str, Any], user_id: Optional[int] = None) -> None:
    """Save prediction to database."""
    try:
        prediction = Prediction(
            user_id=user_id,
            student_payload=json.dumps(student_payload),
            prediction=result["prediction"],
            probability=float(result["probability"]),
            reasons=json.dumps(result.get("reasons", [])),
            recommendation=result.get("recommendation", ""),
            counterfactual=json.dumps(result.get("counterfactual_example", {})),
        )
        db.session.add(prediction)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
