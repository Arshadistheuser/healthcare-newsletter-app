"""
Healthcare Intelligence Digest — Main Flask Application
Run with: python app.py
Open: http://localhost:<PORT>

Architecture note: AI scoring runs in a background thread to avoid
Render's 30-second proxy timeout. Frontend polls /api/status for results.
"""

import traceback
import threading
from flask import Flask, render_template, jsonify
from config import SECRET_KEY, DEBUG, PORT
from fetcher import fetch_all_feeds
from ai_scorer import score_and_summarize
from hubspot_email import create_draft_email

app = Flask(__name__)
app.secret_key = SECRET_KEY

# In-memory store for the current session
state = {
    "status": "idle",        # idle | fetching | scoring | ready | error
    "message": "",
    "raw": [],
    "scored": [],
    "error": "",
}


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/fetch")
def api_fetch():
    """Fetch articles from RSS feeds then kick off AI scoring in background."""
    if state["status"] in ("fetching", "scoring"):
        return jsonify({"success": False, "error": "Already running. Please wait."})

    def run():
        try:
            state["status"] = "fetching"
            state["error"] = ""
            state["scored"] = []
            print("\n[1/2] Fetching RSS feeds...")
            articles = fetch_all_feeds(days_back=14)
            state["raw"] = articles
            state["message"] = f"Fetched {len(articles)} articles. Scoring with AI..."

            state["status"] = "scoring"
            print("\n[2/2] Scoring articles with AI...")
            scored = score_and_summarize(articles)
            state["scored"] = scored
            state["status"] = "ready"
            state["message"] = f"Done! {len(scored)} relevant articles curated."
            print(f"  Complete: {len(scored)} articles ready.")
        except Exception as e:
            state["status"] = "error"
            state["error"] = str(e)
            state["message"] = f"Error: {e}"
            print(traceback.format_exc())

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"success": True, "message": "Started. Poll /api/status for progress."})


@app.route("/api/status")
def api_status():
    """Poll this endpoint for fetch+score progress and results."""
    response = {
        "status": state["status"],
        "message": state["message"],
        "error": state["error"],
        "raw_count": len(state["raw"]),
        "scored_count": len(state["scored"]),
    }

    if state["status"] == "ready" and state["scored"]:
        articles_json = []
        for art in state["scored"]:
            articles_json.append({
                "title": art["title"],
                "link": art["link"],
                "summary": art["summary"],
                "ai_summary": art["ai_summary"],
                "published_str": art["published_str"],
                "source": art["source"],
                "segment": art["segment"],
                "relevance_score": art["relevance_score"],
                "influencers": art["influencers"],
            })
        response["articles"] = articles_json

    return jsonify(response)


@app.route("/api/hubspot", methods=["POST"])
def api_hubspot():
    """Push curated newsletter to HubSpot as a draft marketing email."""
    try:
        scored = state["scored"]
        if not scored:
            return jsonify({"success": False, "message": "No scored articles. Fetch and score first."})

        print("\n[HubSpot] Creating draft marketing email...")
        result = create_draft_email(scored)
        return jsonify(result)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/debug")
def api_debug():
    """Debug endpoint."""
    from config import USE_OLLAMA, GROQ_API_KEY, OLLAMA_MODEL
    return jsonify({
        "USE_OLLAMA": USE_OLLAMA,
        "OLLAMA_MODEL": OLLAMA_MODEL,
        "GROQ_API_KEY_SET": bool(GROQ_API_KEY),
        "state_status": state["status"],
        "raw_count": len(state["raw"]),
        "scored_count": len(state["scored"]),
    })


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Healthcare Intelligence Digest")
    print(f"  Open: http://localhost:{PORT}")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG, use_reloader=False)
