"""
RSS Feed Fetcher — pulls articles from all configured healthcare sources.
Handles both direct RSS feeds and Google News RSS fallbacks.
"""

import feedparser
import re
import time
from datetime import datetime, timedelta
from feeds import FEED_SOURCES

# Set a user-agent so sites don't block us
feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) KOR-Healthcare-Newsletter/1.0"


def fetch_all_feeds(days_back=14):
    """Fetch articles from all RSS feeds published within the last N days."""
    cutoff = datetime.now() - timedelta(days=days_back)
    all_articles = []
    seen_links = set()  # Deduplicate

    for source in FEED_SOURCES:
        try:
            articles = fetch_single_feed(source, cutoff)
            for art in articles:
                # Deduplicate by link
                if art["link"] not in seen_links:
                    seen_links.add(art["link"])
                    all_articles.append(art)
        except Exception as e:
            print(f"  [WARN] Failed to fetch {source['name']}: {e}")

    all_articles.sort(key=lambda a: a["published"], reverse=True)
    print(f"\n  Total articles fetched: {len(all_articles)}")
    return all_articles


def fetch_single_feed(source, cutoff):
    """Fetch and parse a single RSS feed."""
    print(f"  Fetching: {source['name']}...")
    feed = feedparser.parse(source["rss"])
    articles = []

    if feed.bozo and len(feed.entries) == 0:
        print(f"    [WARN] Feed error for {source['name']}: {feed.get('bozo_exception', 'unknown')}")
        return []

    for entry in feed.entries:
        published = parse_date(entry)
        if published and published < cutoff:
            continue

        # For Google News RSS, the real link is sometimes in the <source> tag
        link = entry.get("link", "")
        # Google News wraps links — the entry link redirects to the real article

        title = entry.get("title", "Untitled")
        # Google News sometimes prefixes title with source name, clean it
        title = re.sub(r"\s*-\s*[^-]+$", "", title).strip() if " - " in title else title

        article = {
            "title": title,
            "link": link,
            "summary": clean_summary(entry.get("summary", entry.get("description", ""))),
            "published": published or datetime.now(),
            "published_str": published.strftime("%b %d, %Y") if published else "Recent",
            "source": source["name"],
            "segment": source["segment"],
            "relevance_score": 0,
            "ai_summary": "",
            "influencers": [],
        }
        articles.append(article)

    print(f"    Found {len(articles)} recent articles")
    return articles


def parse_date(entry):
    """Extract and parse the publication date from a feed entry."""
    date_fields = ["published_parsed", "updated_parsed", "created_parsed"]
    for field in date_fields:
        parsed = entry.get(field)
        if parsed:
            try:
                return datetime(*parsed[:6])
            except (TypeError, ValueError):
                continue
    return None


def clean_summary(text):
    """Strip HTML tags from summary text."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"&\w+;", " ", clean)  # HTML entities
    clean = re.sub(r"\s+", " ", clean).strip()
    if len(clean) > 500:
        clean = clean[:500] + "..."
    return clean
