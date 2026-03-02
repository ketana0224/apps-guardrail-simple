import os
import sys
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


def check(condition: bool, message: str) -> None:
    if condition:
        print(f"[PASS] {message}")
    else:
        print(f"[FAIL] {message}")
        raise SystemExit(1)


def request_json(method: str, url: str, **kwargs: Any) -> tuple[int, Any]:
    response = requests.request(method=method, url=url, timeout=15, **kwargs)
    try:
        body = response.json()
    except ValueError:
        body = response.text
    return response.status_code, body


def run(base_url: str, skip_ai_invoke: bool, invoke_input: str) -> None:
    base_url = base_url.rstrip("/")

    status, body = request_json("GET", f"{base_url}/health")
    check(status == 200, "GET /health returns 200")
    check(isinstance(body, dict) and body.get("status") == "ok", "GET /health body has {status: ok}")

    status, body = request_json("POST", f"{base_url}/guardrail/check", json={"text": "hello world"})
    check(status == 200, "POST /guardrail/check(normal) returns 200")
    check(isinstance(body, dict) and body.get("allowed") is True, "normal text is allowed")

    status, body = request_json("POST", f"{base_url}/guardrail/check", json={"text": "this is blocked"})
    check(status == 200, "POST /guardrail/check(blocked keyword) returns 200")
    check(isinstance(body, dict) and body.get("allowed") is False, "blocked keyword is denied")

    if not skip_ai_invoke:
        status, body = request_json("POST", f"{base_url}/guardrail/invoke", json={"input": invoke_input})
        check(status == 200, "POST /guardrail/invoke returns 200")
        output = body.get("output", {}) if isinstance(body, dict) else {}
        valid_outputs = {
            ("block", "block"),
            ("false", "false"),
            ("true", "true"),
        }
        check(
            isinstance(body, dict)
            and body.get("guardrail", {}).get("input") == invoke_input
            and (output.get("status"), output.get("reasons")) in valid_outputs,
            "POST /guardrail/invoke returns one of random output patterns",
        )
        print(f"[INFO] /guardrail/invoke status={status}, body={body}")

    print("\nAll checks completed.")


def main() -> None:
    base_url = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")
    skip_ai_invoke = os.getenv("TEST_SKIP_INVOKE", "false").lower() == "true"
    invoke_input = os.getenv("TEST_INPUT", "hello")

    try:
        run(base_url=base_url, skip_ai_invoke=skip_ai_invoke, invoke_input=invoke_input)
    except requests.RequestException as exc:
        print(f"[FAIL] Request error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
