# Healthcare Intelligence Digest

AI-powered fortnightly newsletter for KOR's healthcare team — curates top articles from 15 healthcare publications, scores them for KOR relevance using AI, and pushes a draft email to HubSpot.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open: `http://localhost:5123`

## Environment variables

Copy `.env.example` to `.env` and fill in:

```
GROQ_API_KEY=           # From https://console.groq.com (used when USE_OLLAMA=false)
HUBSPOT_ACCESS_TOKEN=   # HubSpot Private App token (Marketing Email scope)
USE_OLLAMA=false        # Set true to use local Ollama instead of Groq
OLLAMA_MODEL=qwen2.5:7b
```

## Deploy to Render

The app is configured for Render with `render.yaml`. Set these environment variables in Render dashboard:
- `GROQ_API_KEY` (required — Render uses Groq, not Ollama)
- `HUBSPOT_ACCESS_TOKEN` (required for HubSpot push)
- `USE_OLLAMA=false`
