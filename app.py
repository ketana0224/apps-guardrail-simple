import os
import random
from typing import Any

import requests
from flask import Flask, jsonify, request
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)


def evaluate_input(text: str) -> dict[str, Any]:
    blocked_keywords = ["forbidden", "blocked"]
    matched = [keyword for keyword in blocked_keywords if keyword in text.lower()]
    return {
        "allowed": len(matched) == 0,
        "reasons": ["placeholder-input-rule-matched"] if matched else [],
    }


def evaluate_output(text: str) -> dict[str, Any]:
    blocked_keywords = ["unsafe-output"]
    matched = [keyword for keyword in blocked_keywords if keyword in text.lower()]
    return {
        "allowed": len(matched) == 0,
        "reasons": ["placeholder-output-rule-matched"] if matched else [],
    }


def call_ai_api(prompt: str, context: str | None) -> dict[str, Any]:
    if os.getenv("AI_MOCK_MODE", "false").lower() == "true":
        simulated = f"[mock-ai] {prompt}"
        return {"raw": {"text": simulated, "context": context}, "text": simulated}

    ai_api_url = os.getenv("AI_API_URL")
    ai_api_key = os.getenv("AI_API_KEY")
    ai_api_timeout = int(os.getenv("AI_API_TIMEOUT", "20"))

    if not ai_api_url:
        raise RuntimeError("AI_API_URL is not configured")

    headers = {"Content-Type": "application/json"}
    if ai_api_key:
        headers["Authorization"] = f"Bearer {ai_api_key}"

    payload = {"prompt": prompt, "context": context}

    response = requests.post(ai_api_url, headers=headers, json=payload, timeout=ai_api_timeout)
    response.raise_for_status()
    data = response.json()

    text = data.get("text") if isinstance(data, dict) else None
    if not text:
        text = str(data)

    return {"raw": data, "text": text}


@app.get("/health")
def health() -> Any:
    return jsonify({"status": "ok"}), 200


@app.post("/guardrail/check")
def guardrail_check() -> Any:
    body = request.get_json(silent=True) or {}
    text = body.get("text")

    if not text or not isinstance(text, str):
        return jsonify({"error": "text is required"}), 400

    result = evaluate_input(text)
    return jsonify(result), 200


@app.post("/guardrail/invoke")
def ai_invoke() -> Any:
    body = request.get_json(silent=True) or {}
    input_value = body.get("input")

    if not input_value or not isinstance(input_value, str):
        return jsonify({"error": "input is required"}), 400

    output = random.choice(
        [
            {
                "status": "block",
                "reasons": "block",
            },
            {
                "status": "false",
                "reasons": "false",
            },
            {
                "status": "true",
                "reasons": "true",
            },
        ]
    )

    return (
        jsonify(
            {
                "guardrail": {
                    "input": input_value,
                },
                "output": output,
            }
        ),
        200,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
