from __future__ import annotations

import logging
import os
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request

from alerts import build_alert_payload, should_alert
from gemini_api import call_gemini
from storage import save_prediction
from utils import (
    StudentFeatures,
    build_prompt,
    extract_first_json_block,
    validate_response,
)

app = Flask(
    __name__, template_folder="../templates", static_folder="../static"
)
logging.basicConfig(level=logging.INFO)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.post("/predict")
def predict() -> Any:
    try:
        payload = request.get_json(force=True)
    except Exception as exc:  # pragma: no cover - defensive
        return jsonify({"error": "Invalid JSON payload", "details": str(exc)}), 400

    try:
        student_features = StudentFeatures.from_payload(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    prompt = build_prompt(student_features)
    try:
        raw_response = call_gemini(prompt)
        parsed = extract_first_json_block(raw_response)
        result = validate_response(parsed)
    except Exception as exc:
        logging.exception("Gemini failure")
        return (
            jsonify({
                "error": "Gemini parsing failed",
                "details": str(exc),
                "raw": raw_response if "raw_response" in locals() else None,
            }),
            502,
        )

    try:
        save_prediction(student_features.to_prompt_dict(), result)
    except Exception as exc:
        logging.warning("Could not save prediction: %s", exc)

    alert = None
    if should_alert(result["probability"]):
        alert = build_alert_payload(student_features.to_prompt_dict(), result)

    return jsonify({"result": result, "alert": alert})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
