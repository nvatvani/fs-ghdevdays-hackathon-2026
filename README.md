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

Open `http://127.0.0.1:5000`. Set `MODEL_URL`, `MODEL_NAME`, `MODEL_TIMEOUT`, or
`PORT` as environment variables to override the defaults.
