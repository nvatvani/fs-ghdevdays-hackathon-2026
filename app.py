import os

import requests
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)

MODEL_URL = os.getenv("MODEL_URL", "http://localhost:8080/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma-4-e4b-it")
REQUEST_TIMEOUT = float(os.getenv("MODEL_TIMEOUT", "90"))

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


@app.post("/api/roast")
def roast():
    payload = request.get_json(silent=True) or {}
    idea = payload.get("idea", "")

    if not isinstance(idea, str):
        return jsonify(error="Idea must be text."), 400

    idea = idea.strip()
    if not idea:
        return jsonify(error="Paste an idea first. The model cannot roast a vacuum."), 400
    if len(idea) > 8000:
        return jsonify(error="Keep the pitch under 8,000 characters so there is room for the roast."), 400

    try:
        response = requests.post(
            MODEL_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Roast this hackathon idea:\n\n{idea}"},
                ],
                "temperature": 0.85,
                "max_tokens": 700,
                "stream": False,
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        return jsonify(error="The local model took too long. Try a shorter pitch or check that the server is responsive."), 504
    except requests.exceptions.ConnectionError:
        return jsonify(error=f"Could not reach the local model at {MODEL_URL}. Start the model server and try again."), 503
    except (requests.exceptions.RequestException, ValueError, KeyError, IndexError) as exc:
        app.logger.exception("Model request failed")
        return jsonify(error=f"The model returned an unusable response: {exc}"), 502

    return jsonify(roast=content)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
