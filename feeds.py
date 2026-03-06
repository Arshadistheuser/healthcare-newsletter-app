"""
RSS Feed sources for Healthcare newsletters — organized by sub-segment.
Each source has a name, segment, and RSS feed URL.

Sources are based on the Sales Ops team's curated list of top healthcare
newsletters across key sub-industries.

For sites without working RSS, we use Google News RSS as a reliable fallback.
Google News RSS format:
https://news.google.com/rss/search?q=site:example.com+when:14d&hl=en-US&gl=US&ceid=US:en
"""


def _google_news_rss(site, extra_query=""):
    """Generate a Google News RSS URL for a specific site."""
    query = f"site:{site}"
    if extra_query:
        query += f"+{extra_query}"
    query += "+when:14d"
    return f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


FEED_SOURCES = [
    # ══════════════════════════════════════════════════════════
    # BROAD HEALTHCARE NEWS & INDUSTRY TRENDS
    # ══════════════════════════════════════════════════════════

    # Healthcare Dive — Industry insights on healthcare business, policy, IT
    {"name": "Healthcare Dive", "segment": "Broad Healthcare News & Industry Trends",
     "rss": "https://www.healthcaredive.com/feeds/news/"},

    # Modern Healthcare — Daily news on policy, business, data, research
    {"name": "Modern Healthcare", "segment": "Broad Healthcare News & Industry Trends",
     "rss": _google_news_rss("modernhealthcare.com", "healthcare")},

    # Fierce Healthcare — Industry updates for executives and decision-makers
    {"name": "Fierce Healthcare", "segment": "Broad Healthcare News & Industry Trends",
     "rss": "https://www.fiercehealthcare.com/rss/xml"},

    # Becker's Hospital Review — Hospital operations, finance, leadership
    # (Direct feed blocked; using Google News fallback)
    {"name": "Becker's Hospital Review", "segment": "Broad Healthcare News & Industry Trends",
     "rss": _google_news_rss("beckershospitalreview.com", "hospital+healthcare")},

    # Health Affairs — Deep policy analysis and research summaries
    {"name": "Health Affairs", "segment": "Broad Healthcare News & Industry Trends",
     "rss": _google_news_rss("healthaffairs.org", "health+policy")},

    # KFF Health News — Key health policy developments
    {"name": "KFF Health News", "segment": "Broad Healthcare News & Industry Trends",
     "rss": "https://kffhealthnews.org/feed/"},

    # ══════════════════════════════════════════════════════════
    # LEADERSHIP, IT & OPERATIONAL NEWS
    # ══════════════════════════════════════════════════════════

    # HealthLeaders Media — Leadership insights, strategies, management trends
    {"name": "HealthLeaders Media", "segment": "Leadership, IT & Operational News",
     "rss": _google_news_rss("healthleadersmedia.com", "healthcare+leadership")},

    # Healthcare IT News — IT, digital transformation, cybersecurity, interoperability
    # (Direct feed malformed; using Google News fallback)
    {"name": "Healthcare IT News", "segment": "Leadership, IT & Operational News",
     "rss": _google_news_rss("healthcareitnews.com", "healthcare+IT+digital")},

    # Symplr — Healthcare operations, performance, workflow
    {"name": "Symplr", "segment": "Leadership, IT & Operational News",
     "rss": _google_news_rss("symplr.com", "healthcare+operations")},

    # ══════════════════════════════════════════════════════════
    # BUSINESS & SECTOR-SPECIFIC NEWSLETTERS
    # ══════════════════════════════════════════════════════════

    # HealthExecWire — Business and policy updates (Accountable Care, Pop Health)
    {"name": "HealthExecWire", "segment": "Business & Sector-Specific",
     "rss": _google_news_rss("healthexec.com", "healthcare+business")},

    # ══════════════════════════════════════════════════════════
    # LEADERSHIP / DIGITAL HEALTH
    # ══════════════════════════════════════════════════════════

    # Health Tech Nerds — Digital health, payor/provider models, startups
    {"name": "Health Tech Nerds", "segment": "Leadership / Digital Health",
     "rss": _google_news_rss("healthtechnerds.com", "digital+health")},

    # ══════════════════════════════════════════════════════════
    # BONUS: Additional high-value healthcare sources
    # (broader coverage to enrich the newsletter)
    # ══════════════════════════════════════════════════════════

    # HIMSS — Health IT conference org, publishes deep digital health content
    {"name": "HIMSS", "segment": "Leadership / Digital Health",
     "rss": _google_news_rss("himss.org", "health+IT+digital")},

    # MedCity News — Healthcare business, innovation, startups
    {"name": "MedCity News", "segment": "Business & Sector-Specific",
     "rss": "https://medcitynews.com/feed/"},

    # Healthcare Finance News — Financial topics, revenue cycle, reimbursement
    # (Direct feed malformed; using Google News fallback)
    {"name": "Healthcare Finance News", "segment": "Business & Sector-Specific",
     "rss": _google_news_rss("healthcarefinancenews.com", "healthcare+finance")},

    # STAT News — Life sciences, pharma, biotech, clinical research
    {"name": "STAT News", "segment": "Broad Healthcare News & Industry Trends",
     "rss": _google_news_rss("statnews.com", "healthcare+pharma")},
]
