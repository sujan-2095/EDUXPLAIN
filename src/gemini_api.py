"""Wrapper around google-genai Gemini client."""
from __future__ import annotations

import os
from typing import Any

from google import genai

API_KEY_ENV = "GEMINI_API_KEY"


def _configure_client() -> genai.Client:
    api_key = os.getenv(API_KEY_ENV)
    if not api_key:
        raise RuntimeError(f"Environment variable {API_KEY_ENV} is not set")
    return genai.Client(api_key=api_key)


client = None


def get_client() -> genai.Client:
    global client
    if client is None:
        client = _configure_client()
    return client


def call_gemini(prompt: str, model: str = "gemini-2.0-flash") -> str:
    response = get_client().models.generate_content(
        model=model,
        contents=prompt,
        config={"temperature": 0.3, "max_output_tokens": 400},
    )
    return response.text or ""
