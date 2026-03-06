"""
AI integration — scores healthcare articles for KOR relevance,
generates summaries, and extracts influencer mentions.

Supports TWO backends (configured in config.py):
  1. OLLAMA (local, free, no rate limits) — recommended
  2. GROQ  (cloud, free tier, fast) — fallback

Uses a 2-step approach:
  1. KEYWORD pre-filter (free, instant) — removes obviously irrelevant articles
  2. LLM scoring (Ollama or Groq) — only on the pre-filtered subset
"""

import json
import re
import time
import requests
from config import (
    GROQ_API_KEY, KOR_KEYWORDS, KOR_CONTEXT, RELEVANCE_THRESHOLD,
    OLLAMA_MODEL, OLLAMA_URL, USE_OLLAMA,
)


def _call_llm(prompt):
    """
    Call the configured LLM backend (Ollama or Groq).
    Returns the assistant's text response.
    """
    if USE_OLLAMA:
        return _call_ollama(prompt)
    else:
        return _call_groq(prompt)


def _call_ollama(prompt):
    """Call Ollama's local API (OpenAI-compatible endpoint)."""
    url = f"{OLLAMA_URL}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 4000,
        },
    }
    resp = requests.post(url, json=payload, timeout=300)
    resp.raise_for_status()
    data = resp.json()
    return data["message"]["content"].strip()


def _call_groq(prompt):
    """Call Groq's cloud API as fallback."""
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000,
    )
    return response.choices[0].message.content.strip()


def keyword_prefilter(articles):
    """
    Step 1: Fast keyword-based pre-filter.
    Keeps only articles that mention at least one KOR-relevant keyword.
    This reduces hundreds of articles to ~50-80, saving LLM calls.
    """
    keywords_lower = [kw.lower() for kw in KOR_KEYWORDS]
    filtered = []

    for art in articles:
        text = (art["title"] + " " + art["summary"]).lower()
        matches = sum(1 for kw in keywords_lower if kw in text)
        if matches > 0:
            art["keyword_matches"] = matches
            filtered.append(art)

    # Sort by keyword matches (most relevant first), take top 60
    filtered.sort(key=lambda a: a.get("keyword_matches", 0), reverse=True)
    if len(filtered) > 60:
        filtered = filtered[:60]

    print(f"  Keyword pre-filter: {len(articles)} -> {len(filtered)} articles")
    return filtered


def score_and_summarize(articles, max_articles=30):
    """Score all articles for relevance and summarize the top ones."""
    # Step 1: Keyword pre-filter (free, instant)
    filtered = keyword_prefilter(articles)

    if not filtered:
        print("  No articles passed keyword pre-filter.")
        return []

    # Step 2: LLM scoring on the filtered subset
    # Process in batches of 10 (smaller batches = better quality from local LLMs)
    batch_size = 8 if USE_OLLAMA else 10
    scored = []
    total_batches = (len(filtered) + batch_size - 1) // batch_size

    for i in range(0, len(filtered), batch_size):
        batch_num = (i // batch_size) + 1
        batch = filtered[i:i + batch_size]
        print(f"  AI scoring batch {batch_num}/{total_batches} ({len(batch)} articles)...")

        batch_results = score_batch(batch)
        scored.extend(batch_results)

        # Delay between batches (less needed for Ollama since it's local)
        if i + batch_size < len(filtered):
            time.sleep(1 if USE_OLLAMA else 3)

    # Sort by relevance and take top articles
    scored.sort(key=lambda a: a["relevance_score"], reverse=True)
    top_articles = [a for a in scored if a["relevance_score"] >= RELEVANCE_THRESHOLD]

    if len(top_articles) > max_articles:
        top_articles = top_articles[:max_articles]

    print(f"  AI scored {len(scored)} articles, {len(top_articles)} passed relevance threshold ({RELEVANCE_THRESHOLD}+)")
    return top_articles


def score_batch(articles):
    """Score and summarize a batch of articles using the configured LLM."""
    articles_text = ""
    for idx, art in enumerate(articles):
        articles_text += f"""
---ARTICLE {idx}---
Title: {art['title']}
Source: {art['source']}
Segment: {art['segment']}
Summary: {art['summary'][:300]}
"""

    prompt = f"""You are an AI analyst for Korcomptenz (KOR). Here is KOR's profile:

{KOR_CONTEXT}

Analyze these healthcare industry articles and return a JSON array. For EACH article, provide:

1. "index": the article index number

2. "relevance_score": 1-10 score based on how relevant this article is to KOR. Score HIGH (8-10) if the article covers:
   - Technologies KOR implements (ERP, Dynamics 365, SAP, Salesforce, Azure, AWS, AI/ML, Power BI)
   - Digital transformation challenges KOR solves (legacy modernization, cloud migration, data analytics, interoperability)
   - Healthcare IT topics (EHR, telehealth, FHIR, cybersecurity, HIPAA, revenue cycle management)
   - Trends that create demand for KOR's services (AI adoption, cloud migration, digital health, value-based care)
   - Competitor or partner moves (Microsoft, SAP, Salesforce, AWS, Epic, Cerner/Oracle Health ecosystem)
   Score MEDIUM (5-7) for general healthcare operations, policy, or industry news.
   Score LOW (1-4) for purely clinical/medical articles with no connection to technology or KOR's services.

3. "ai_summary": A 2-3 sentence summary written for KOR's Healthcare team. Highlight:
   - Why this matters for healthcare leaders and IT decision-makers
   - Any connection to KOR's capabilities (e.g., "This trend aligns with KOR's Dynamics 365/Azure/AI practice")
   - Actionable insight the sales team can use in conversations with healthcare prospects

4. "influencers": Array of people, companies, or organizations mentioned who are notable movers & shakers in healthcare. Include executives, analysts, vendors, payers, health systems, or industry bodies. Empty array if none are apparent.

Return ONLY valid JSON array, no markdown, no explanation. Example format:
[{{"index": 0, "relevance_score": 8, "ai_summary": "...", "influencers": ["Person A", "Company B"]}}]

{articles_text}
"""

    try:
        text = _call_llm(prompt)

        # Clean up potential markdown wrapping
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        # Try to extract JSON array if there's extra text around it
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            text = json_match.group(0)

        results = json.loads(text)

        for result in results:
            idx = result.get("index", 0)
            if 0 <= idx < len(articles):
                articles[idx]["relevance_score"] = result.get("relevance_score", 0)
                articles[idx]["ai_summary"] = result.get("ai_summary", "")
                articles[idx]["influencers"] = result.get("influencers", [])

    except json.JSONDecodeError as e:
        print(f"    [WARN] Failed to parse AI response: {e}")
        # Try line-by-line JSON parsing as fallback
        _try_line_parse(text, articles)
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate" in error_str.lower():
            print(f"    [WARN] Rate limited. Waiting 30 seconds...")
            time.sleep(30)
            # Retry once
            try:
                text = _call_llm(prompt)
                if text.startswith("```"):
                    text = text.split("\n", 1)[1]
                    if text.endswith("```"):
                        text = text[:-3]
                    text = text.strip()
                json_match = re.search(r'\[.*\]', text, re.DOTALL)
                if json_match:
                    text = json_match.group(0)
                results = json.loads(text)
                for result in results:
                    idx = result.get("index", 0)
                    if 0 <= idx < len(articles):
                        articles[idx]["relevance_score"] = result.get("relevance_score", 0)
                        articles[idx]["ai_summary"] = result.get("ai_summary", "")
                        articles[idx]["influencers"] = result.get("influencers", [])
            except Exception as retry_err:
                print(f"    [WARN] Retry also failed: {retry_err}")
        else:
            print(f"    [WARN] AI API error: {e}")

    return articles


def _try_line_parse(text, articles):
    """Fallback: try to parse individual JSON objects from malformed output."""
    try:
        for line in text.split("\n"):
            line = line.strip().rstrip(",")
            if line.startswith("{") and line.endswith("}"):
                obj = json.loads(line)
                idx = obj.get("index", -1)
                if 0 <= idx < len(articles):
                    articles[idx]["relevance_score"] = obj.get("relevance_score", 0)
                    articles[idx]["ai_summary"] = obj.get("ai_summary", "")
                    articles[idx]["influencers"] = obj.get("influencers", [])
    except Exception:
        pass
