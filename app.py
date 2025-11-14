from __future__ import annotations

import logging
import os
import secrets
from functools import wraps
from typing import Any, Dict

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from src.alerts import build_alert_payload, should_alert
from src.auth import authenticate_user, get_user_by_id, register_user
from src.gemini_api import call_gemini
from src.storage import save_prediction
from src.utils import (
    StudentFeatures,
    build_prompt,
    extract_first_json_block,
    validate_response,
)

app = Flask(
    __name__, template_folder="templates", static_folder="static"
)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))
logging.basicConfig(level=logging.INFO)


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index() -> str:
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = get_user_by_id(session["user_id"])
    return render_template("index.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login() -> Any:
    if "user_id" in session:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        user = authenticate_user(username, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid username or password")
    
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register() -> Any:
    if "user_id" in session:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        success, message = register_user(username, email, password)
        if success:
            user = authenticate_user(username, password)
            if user:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("index"))
        else:
            return render_template("register.html", error=message)
    
    return render_template("register.html")


@app.route("/logout")
def logout() -> Any:
    session.clear()
    return redirect(url_for("login"))


@app.post("/predict")
@login_required
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
        user_id = session.get("user_id")
        save_prediction(student_features.to_prompt_dict(), result, user_id=user_id)
    except Exception as exc:
        logging.warning("Could not save prediction: %s", exc)

    alert = None
    if should_alert(result["probability"]):
        alert = build_alert_payload(student_features.to_prompt_dict(), result)

    return jsonify({"result": result, "alert": alert})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

