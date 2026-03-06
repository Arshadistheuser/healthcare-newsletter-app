"""
Healthcare Intelligence Digest — Main Flask Application
Run with: python app.py
Open: http://localhost:<PORT>
"""

import traceback
from flask import Flask, render_template, jsonify
from config import SECRET_KEY, DEBUG, PORT
from fetcher import fetch_all_feeds
from ai_scorer import score_and_summarize
from hubspot_email import create_draft_email

app = Flask(__name__)
app.secret_key = SECRET_KEY

# In-memory store for the current session's articles
current_articles = {"raw": [], "scored": []}


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/fetch")
def api_fetch():
    """Fetch articles from all RSS feeds."""
    try:
        print("\n[1/2] Fetching RSS feeds...")
        articles = fetch_all_feeds(days_back=14)
        current_articles["raw"] = articles
        return jsonify({
            "success": True,
            "count": len(articles),
            "message": f"Fetched {len(articles)} articles from RSS feeds.",
        })
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return jsonify({"success": False, "error": str(e), "traceback": tb}), 500


@app.route("/api/score")
def api_score():
    """Score and summarize articles using AI."""
    try:
        raw = current_articles["raw"]
        if not raw:
            return jsonify({"success": False, "error": "No articles fetched yet. Click Fetch first."})

        print("\n[2/2] Scoring articles with AI...")
        scored = score_and_summarize(raw)
        current_articles["scored"] = scored

        articles_json = []
        for art in scored:
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

        return jsonify({
            "success": True,
            "count": len(articles_json),
            "articles": articles_json,
        })
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return jsonify({"success": False, "error": str(e), "traceback": tb}), 500


@app.route("/api/hubspot", methods=["POST"])
def api_hubspot():
    """Push curated newsletter to HubSpot as a draft marketing email."""
    try:
        scored = current_articles["scored"]
        if not scored:
            return jsonify({"success": False, "message": "No scored articles. Fetch and score first."})

        print("\n[HubSpot] Creating draft marketing email...")
        result = create_draft_email(scored)
        return jsonify(result)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return jsonify({"success": False, "message": str(e), "traceback": tb}), 500


@app.route("/api/debug")
def api_debug():
    """Debug endpoint — tests Groq connection and shows config."""
    import os
    from config import USE_OLLAMA, GROQ_API_KEY, OLLAMA_MODEL
    result = {
        "USE_OLLAMA": USE_OLLAMA,
        "OLLAMA_MODEL": OLLAMA_MODEL,
        "GROQ_API_KEY_SET": bool(GROQ_API_KEY),
        "raw_articles_in_memory": len(current_articles["raw"]),
    }
    # Quick Groq test
    if not USE_OLLAMA and GROQ_API_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5,
            )
            result["groq_test"] = resp.choices[0].message.content
        except Exception as e:
            result["groq_error"] = str(e)
    return jsonify(result)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Healthcare Intelligence Digest")
    print(f"  Open: http://localhost:{PORT}")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG, use_reloader=False)
