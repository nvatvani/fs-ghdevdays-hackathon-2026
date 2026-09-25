# Roast My Pitch

A small Flask webapp that sends hackathon ideas to a locally running
`gemma-4-e4b-it` model and returns an aggressively sarcastic, useful critique.

## Run it

1. Start an OpenAI-compatible local model server at
   `http://localhost:8080/v1/chat/completions`.
2. Install the Python dependencies with `uv`:

   ```bash
   uv sync
   ```

3. Start Flask:

   ```bash
   uv run python app.py
   ```

Open `http://127.0.0.1:5000`. The header checks the model endpoint every three
seconds and shows whether it is reachable. Open the vertical **SETTINGS** tab on
the right to override the model URL, model name, request timeout, and API key
for this browser. Settings are stored locally in the browser, and the API key
defaults to an empty string for unauthenticated local servers. Environment
variables remain available for server-wide defaults: `MODEL_URL`, `MODEL_NAME`,
`MODEL_TIMEOUT`, `MODEL_HEALTH_TIMEOUT`, `API_KEY`, and `PORT`.
