import os
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)

MODEL_URL = os.getenv("MODEL_URL", "http://localhost:8080/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma-4-e4b-it")
REQUEST_TIMEOUT = float(os.getenv("MODEL_TIMEOUT", "90"))
HEALTH_TIMEOUT = float(os.getenv("MODEL_HEALTH_TIMEOUT", "3"))
SERVER_PORT = int(os.getenv("PORT", "5000"))
API_KEY = os.getenv("API_KEY", "")

SYSTEM_PROMPT = """You are Roast My Pitch, an incisive hackathon idea evaluator.
Your job is to aggressively roast the idea while still giving feedback the builder
can use. Be sarcastic, funny, and specific; punch up at the idea's assumptions,
scope, buzzwords, and execution gaps, never at protected traits or the person.
Do not be hateful, threatening, or abusive. Do not invent market data.

Use this format:
VERDICT: one short, brutally funny sentence

THE ROAST:
2-4 short paragraphs of sharp, concrete criticism.

THE ACTUAL PROBLEM:
State the core user problem the idea appears to target, or say what is missing.

MAKE IT LESS BAD:
Give exactly 3 practical changes that would make the idea more compelling for a
hackathon. Be direct and avoid generic startup advice.
"""


@app.get("/")
def index():
    return render_template("index.html")


def get_model_config(payload=None):
    payload = payload or {}
    model_url = payload.get("model_url", MODEL_URL)
    model_name = payload.get("model_name", MODEL_NAME)
    request_timeout = payload.get("model_timeout", REQUEST_TIMEOUT)
    api_key = payload.get("api_key", API_KEY)

    if not isinstance(model_url, str) or urlparse(model_url).scheme not in {"http", "https"}:
        raise ValueError("Model URL must start with http:// or https://.")
    if not isinstance(model_name, str) or not model_name.strip():
        raise ValueError("Model name cannot be empty.")
    try:
        request_timeout = float(request_timeout)
    except (TypeError, ValueError) as exc:
        raise ValueError("Model timeout must be a number.") from exc
    if not 1 <= request_timeout <= 300:
        raise ValueError("Model timeout must be between 1 and 300 seconds.")
    if not isinstance(api_key, str):
        raise ValueError("API key must be text.")

    return model_url, model_name.strip(), request_timeout, api_key


def get_models_url(model_url):
    parsed = urlparse(model_url)
    path = parsed.path.rstrip("/")
    if path.endswith("/chat/completions"):
        path = path[: -len("/chat/completions")] + "/models"
    else:
        path = path.rsplit("/", 1)[0] + "/models"
    return parsed._replace(path=path, params="", query="", fragment="").geturl()


@app.get("/api/config")
def config():
    return jsonify(
        model_url=MODEL_URL,
        model_name=MODEL_NAME,
        model_timeout=REQUEST_TIMEOUT,
        api_key=API_KEY,
    )


@app.post("/api/model-status")
def model_status():
    payload = request.get_json(silent=True) or {}
    try:
        model_url, _, request_timeout, api_key = get_model_config(payload)
    except ValueError as exc:
        return jsonify(online=False, error=str(exc)), 400

    try:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        response = requests.get(
            model_url,
            headers=headers,
            timeout=min(HEALTH_TIMEOUT, request_timeout),
        )
        if response.status_code >= 500:
            return jsonify(online=False), 503
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        return jsonify(online=False), 503
    except requests.exceptions.RequestException:
        app.logger.exception("Model health check failed")
        return jsonify(online=False), 502

    return jsonify(online=True)


@app.post("/api/models")
def models():
    payload = request.get_json(silent=True) or {}
    try:
        model_url, _, request_timeout, api_key = get_model_config(payload)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    try:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        response = requests.get(
            get_models_url(model_url),
            headers=headers,
            timeout=request_timeout,
        )
        response.raise_for_status()
        model_data = response.json()
        model_ids = [
            item["id"]
            for item in model_data.get("data", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        ]
    except requests.exceptions.Timeout:
        return jsonify(error="The model list request timed out."), 504
    except requests.exceptions.ConnectionError:
        return jsonify(error="Could not reach the model list endpoint."), 503
    except (requests.exceptions.RequestException, ValueError, AttributeError, KeyError) as exc:
        app.logger.exception("Model list request failed")
        return jsonify(error=f"Could not load available models: {exc}"), 502

    return jsonify(models=model_ids)


@app.post("/api/roast")
def roast():
    payload = request.get_json(silent=True) or {}
    idea = payload.get("idea", "")

    try:
        model_url, model_name, request_timeout, api_key = get_model_config(payload)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    if not isinstance(idea, str):
        return jsonify(error="Idea must be text."), 400

    idea = idea.strip()
    if not idea:
        return jsonify(error="Paste an idea first. The model cannot roast a vacuum."), 400
    if len(idea) > 8000:
        return jsonify(error="Keep the pitch under 8,000 characters so there is room for the roast."), 400

    try:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        response = requests.post(
            model_url,
            headers=headers,
            json={
                "model": model_name,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Roast this hackathon idea:\n\n{idea}"},
                ],
                "temperature": 0.85,
                "max_tokens": 700,
                "stream": False,
            },
            timeout=request_timeout,
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        return jsonify(error="The local model took too long. Try a shorter pitch or check that the server is responsive."), 504
    except requests.exceptions.ConnectionError:
        return jsonify(error=f"Could not reach the configured model at {model_url}. Check the URL and try again."), 503
    except requests.exceptions.HTTPError as exc:
        app.logger.exception("Model rejected roast request")
        try:
            detail = exc.response.json().get("message", str(exc))
        except (ValueError, AttributeError):
            detail = str(exc)
        return jsonify(error=f"The model rejected the request: {detail}"), 502
    except (requests.exceptions.RequestException, ValueError, KeyError, IndexError) as exc:
        app.logger.exception("Model request failed")
        return jsonify(error=f"The model returned an unusable response: {exc}"), 502

    return jsonify(roast=content)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=SERVER_PORT, debug=True)
