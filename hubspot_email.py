"""
HubSpot Marketing Email Integration — creates draft marketing emails
with the curated healthcare newsletter content.

Uses HubSpot's Marketing Email API v3.
Strategy: Create email (gets default template), then PATCH to inject our HTML content.
"""

import requests
import json
from datetime import datetime
from config import HUBSPOT_ACCESS_TOKEN


HUBSPOT_API_BASE = "https://api.hubapi.com"


def get_headers():
    return {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def build_newsletter_html(articles):
    """Build email-safe HTML newsletter content (inline styles, table-based)."""
    today = datetime.now().strftime("%B %d, %Y")

    # Free healthcare-themed stock image (Unsplash - medical/healthcare technology)
    banner_url = "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=700&h=250&fit=crop&crop=center&q=80"

    html = f"""
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:700px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;">
    <tr>
        <td style="padding:0;line-height:0;">
            <img src="{banner_url}" alt="Healthcare Intelligence" width="700" style="width:100%;max-width:700px;height:auto;display:block;border:0;" />
        </td>
    </tr>
    <tr>
        <td style="background:#0f766e;color:white;padding:20px 24px;text-align:center;">
            <h1 style="margin:0;font-size:24px;color:white;">Healthcare Intelligence Digest</h1>
            <p style="margin:6px 0 0;color:#99f6e4;font-size:13px;">Curated by Korcomptenz | {today}</p>
        </td>
    </tr>
"""

    # Group articles by segment
    segments = {}
    for art in articles:
        seg = art["segment"]
        if seg not in segments:
            segments[seg] = []
        segments[seg].append(art)

    for segment, seg_articles in segments.items():
        html += f"""
    <tr>
        <td style="padding:18px 20px 6px;">
            <h2 style="color:#0f766e;font-size:17px;border-bottom:2px solid #14b8a6;padding-bottom:6px;margin:0;">{segment}</h2>
        </td>
    </tr>
"""
        for art in seg_articles:
            score_color = "#22c55e" if art["relevance_score"] >= 8 else "#f59e0b" if art["relevance_score"] >= 6 else "#94a3b8"
            influencer_html = ""
            if art.get("influencers") and len(art["influencers"]) > 0:
                names = ", ".join(str(i) for i in art["influencers"][:3])
                influencer_html = f'<p style="margin:3px 0 0;font-size:11px;color:#6b7280;">Key mentions: {names}</p>'

            html += f"""
    <tr>
        <td style="padding:4px 20px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0fdfa;border-left:4px solid {score_color};">
                <tr>
                    <td style="padding:12px 14px;">
                        <a href="{art['link']}" style="color:#0f766e;text-decoration:none;font-size:14px;font-weight:bold;">{art['title']}</a>
                        <p style="margin:3px 0;font-size:11px;color:#94a3b8;">{art['source']} &middot; {art['published_str']} &middot; Relevance: {art['relevance_score']}/10</p>
                        <p style="margin:5px 0 0;font-size:12px;color:#374151;line-height:1.5;">{art['ai_summary']}</p>
                        {influencer_html}
                    </td>
                </tr>
            </table>
        </td>
    </tr>
"""

    # Influencers summary
    all_influencers = []
    for art in articles:
        for inf in art.get("influencers", []):
            inf_str = str(inf)
            if inf_str not in all_influencers:
                all_influencers.append(inf_str)

    if all_influencers:
        html += f"""
    <tr>
        <td style="padding:16px 20px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0fdfa;">
                <tr>
                    <td style="padding:14px 18px;">
                        <h3 style="color:#0f766e;font-size:15px;margin:0 0 6px;">Movers &amp; Shakers This Period</h3>
                        <p style="font-size:12px;color:#374151;margin:0;">{', '.join(all_influencers[:20])}</p>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
"""

    html += """
    <tr>
        <td style="padding:16px;text-align:center;border-top:1px solid #e2e8f0;">
            <p style="font-size:10px;color:#94a3b8;margin:0;">Curated with AI by Korcomptenz Sales Ops</p>
        </td>
    </tr>
</table>
"""
    return html


def create_draft_email(articles):
    """Create a draft marketing email in HubSpot with newsletter content."""
    html_content = build_newsletter_html(articles)

    today = datetime.now().strftime("%B %d, %Y")
    title = f"Healthcare Intelligence Digest - {today}"
    subject = f"Healthcare Intelligence Digest - {today}"

    # Step 1: Create the email (gets default template)
    create_payload = {
        "name": title,
        "subject": subject,
    }

    url = f"{HUBSPOT_API_BASE}/marketing/v3/emails"
    resp = requests.post(url, headers=get_headers(), json=create_payload)

    if resp.status_code not in (200, 201):
        error_detail = resp.text[:300]
        print(f"  [ERROR] Failed to create email ({resp.status_code}): {error_detail}")
        return {"success": False, "message": f"HubSpot create error ({resp.status_code}): {error_detail}"}

    email = resp.json()
    email_id = email.get("id", "")
    print(f"  Email created with ID: {email_id}")

    # Step 2: PATCH the email to inject our newsletter HTML into the rich_text widget
    content = email.get("content", {})
    widgets = content.get("widgets", {})

    # Find the rich_text widget and replace its HTML
    rich_text_key = None
    for key, widget in widgets.items():
        body = widget.get("body", {})
        if body.get("path") == "@hubspot/rich_text":
            rich_text_key = key
            break

    if rich_text_key:
        widgets[rich_text_key]["body"]["html"] = html_content
    else:
        # If no rich_text widget found, create one
        widgets["module-0-0-0"] = {
            "body": {
                "html": html_content,
                "path": "@hubspot/rich_text",
                "schema_version": 2,
                "css_class": "dnd-module",
            },
            "type": "module",
            "id": "module-0-0-0",
            "name": "module-0-0-0",
            "order": 2,
            "css": {},
            "child_css": {},
            "styles": {"breakpointStyles": {"default": {}, "mobile": {}}},
        }

    content["widgets"] = widgets

    patch_payload = {
        "content": content,
    }

    patch_url = f"{HUBSPOT_API_BASE}/marketing/v3/emails/{email_id}"
    patch_resp = requests.patch(patch_url, headers=get_headers(), json=patch_payload)

    if patch_resp.status_code in (200, 201):
        print(f"  Newsletter content injected into email!")
        return {
            "success": True,
            "email_id": email_id,
            "title": title,
            "edit_url": f"https://app.hubspot.com/email/{email_id}/edit",
            "message": f"Draft email '{title}' created in HubSpot with newsletter content. Open HubSpot to review, select recipients, and send.",
        }
    else:
        error_detail = patch_resp.text[:300]
        print(f"  [WARN] Email created but content patch failed ({patch_resp.status_code}): {error_detail}")
        return {
            "success": True,
            "email_id": email_id,
            "title": title,
            "message": f"Email created but content injection failed. Open HubSpot to manually paste the content. Error: {error_detail}",
        }
