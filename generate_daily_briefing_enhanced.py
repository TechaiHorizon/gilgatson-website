#!/usr/bin/env python3
"""
Enhanced Daily Tech Briefing Generator for gilgatson.com
Fetches REAL news from Hacker News API, Techmeme, and AP News,
then uses LLM only for Gil Gatson's strategic analysis.
"""

import os
import sys
import json
import re
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# ─── Configuration ───────────────────────────────────────────────────────────
REPO_DIR = os.environ.get("REPO_DIR", "/home/ubuntu/gilgatson-website-repo")
BLOG_DIR = os.path.join(REPO_DIR, "src", "pages", "blog")
LOG_FILE = os.path.join(REPO_DIR, "briefing_generator.log")

RELEVANCE_KEYWORDS = [
    "ai", "artificial intelligence", "semiconductor", "chip", "china", "taiwan",
    "tsmc", "nvidia", "deepseek", "export", "sanctions", "openai", "anthropic",
    "llm", "gpu", "intel", "amd", "claude", "gpt", "gemini", "machine learning",
    "neural", "model", "tech war", "tariff", "huawei", "bytedance", "tiktok",
    "compute", "data center", "quantum", "robotics", "autonomous", "regulation",
    "copyright", "open source", "foundry", "wafer", "lithography", "asml",
    "arm", "qualcomm", "broadcom", "apple intelligence", "siri", "alexa",
    "microsoft", "google", "meta", "amazon", "agent", "agi", "safety",
    "alignment", "transformer", "diffusion", "training", "inference",
]

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# NEWS FETCHING — Real sources only
# ═══════════════════════════════════════════════════════════════════════════════

def _is_relevant(text: str) -> bool:
    """Check if text matches any relevance keyword."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in RELEVANCE_KEYWORDS)


def fetch_hackernews(max_stories: int = 60) -> list[dict]:
    """Fetch top stories from Hacker News API and filter for relevance."""
    log.info("Fetching from Hacker News API...")
    stories = []
    try:
        resp = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=15
        )
        resp.raise_for_status()
        top_ids = resp.json()[:max_stories]

        for sid in top_ids:
            try:
                item = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    timeout=10,
                ).json()
                if not item or "title" not in item:
                    continue
                if _is_relevant(item["title"]):
                    stories.append(
                        {
                            "title": item["title"],
                            "url": item.get(
                                "url",
                                f"https://news.ycombinator.com/item?id={sid}",
                            ),
                            "source": "Hacker News",
                            "score": item.get("score", 0),
                            "time": datetime.fromtimestamp(item["time"]),
                        }
                    )
            except Exception:
                continue

        log.info(f"  Hacker News: {len(stories)} relevant stories found")
    except Exception as e:
        log.error(f"  Hacker News fetch failed: {e}")
    return stories


def fetch_techmeme() -> list[dict]:
    """Scrape Techmeme for current tech headlines."""
    log.info("Fetching from Techmeme...")
    stories = []
    try:
        resp = requests.get(
            "https://www.techmeme.com/",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        headlines = soup.select("a.ourh")

        for h in headlines:
            title = h.get_text(strip=True)
            url = h.get("href", "")
            if title and url and _is_relevant(title):
                stories.append(
                    {
                        "title": title,
                        "url": url,
                        "source": "Techmeme",
                        "score": 0,
                        "time": datetime.now(),  # Techmeme doesn't expose timestamps easily
                    }
                )

        log.info(f"  Techmeme: {len(stories)} relevant stories found")
    except Exception as e:
        log.error(f"  Techmeme fetch failed: {e}")
    return stories


def fetch_apnews() -> list[dict]:
    """Scrape AP News technology hub for headlines."""
    log.info("Fetching from AP News...")
    stories = []
    try:
        resp = requests.get(
            "https://apnews.com/hub/technology",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a")

        for a in links:
            text = a.get_text(strip=True)
            href = a.get("href", "")
            if text and len(text) > 25 and "/article/" in href:
                if not href.startswith("http"):
                    href = "https://apnews.com" + href
                if _is_relevant(text):
                    stories.append(
                        {
                            "title": text,
                            "url": href,
                            "source": "AP News",
                            "score": 0,
                            "time": datetime.now(),
                        }
                    )

        log.info(f"  AP News: {len(stories)} relevant stories found")
    except Exception as e:
        log.error(f"  AP News fetch failed: {e}")
    return stories


def fetch_arstechnica() -> list[dict]:
    """Scrape Ars Technica for AI/tech headlines."""
    log.info("Fetching from Ars Technica...")
    stories = []
    try:
        resp = requests.get(
            "https://arstechnica.com/",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a")
        seen_urls = set()

        for a in links:
            text = a.get_text(strip=True)
            href = a.get("href", "")
            if (
                text
                and len(text) > 25
                and href
                and href.startswith("https://arstechnica.com/")
                and href not in seen_urls
                and _is_relevant(text)
            ):
                seen_urls.add(href)
                stories.append(
                    {
                        "title": text,
                        "url": href,
                        "source": "Ars Technica",
                        "score": 0,
                        "time": datetime.now(),
                    }
                )

        log.info(f"  Ars Technica: {len(stories)} relevant stories found")
    except Exception as e:
        log.error(f"  Ars Technica fetch failed: {e}")
    return stories


# High-priority keywords that define Gil Gatson's core topics
CORE_KEYWORDS = [
    "semiconductor", "chip", "china", "taiwan", "tsmc", "nvidia", "deepseek",
    "export", "sanctions", "huawei", "tech war", "tariff", "asml", "foundry",
    "wafer", "lithography", "intel", "amd", "qualcomm", "broadcom", "arm",
    "openai", "anthropic", "google", "meta", "microsoft", "amazon",
    "ai", "artificial intelligence", "llm", "gpu", "agi", "safety",
    "regulation", "data center", "compute", "training", "inference",
    "geopolit", "trade", "billion", "funding", "invest",
]


def _relevance_score(title: str) -> int:
    """Score a story's relevance to Gil Gatson's core topics."""
    title_lower = title.lower()
    score = 0
    for kw in CORE_KEYWORDS:
        if kw in title_lower:
            score += 1
    return score


def deduplicate_stories(stories: list[dict]) -> list[dict]:
    """Remove duplicate stories based on URL and similar titles."""
    seen_urls = set()
    seen_titles = set()
    unique = []
    for s in stories:
        url_key = s["url"].split("?")[0].rstrip("/")
        # Simple title dedup: first 50 chars lowered
        title_key = s["title"][:50].lower().strip()
        if url_key not in seen_urls and title_key not in seen_titles:
            seen_urls.add(url_key)
            seen_titles.add(title_key)
            unique.append(s)
    return unique


def fetch_all_news() -> list[dict]:
    """Fetch from all sources, deduplicate, and rank."""
    all_stories = []
    all_stories.extend(fetch_hackernews())
    all_stories.extend(fetch_techmeme())
    all_stories.extend(fetch_apnews())
    all_stories.extend(fetch_arstechnica())

    # Deduplicate
    unique = deduplicate_stories(all_stories)

    # Sort by relevance to Gil Gatson's core topics first, then by HN score as tiebreaker
    for s in unique:
        s["relevance"] = _relevance_score(s["title"])
    unique.sort(key=lambda x: (x["relevance"], x.get("score", 0)), reverse=True)

    log.info(f"Total unique relevant stories: {len(unique)}")
    return unique


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT GENERATION — LLM for analysis only, NOT for news
# ═══════════════════════════════════════════════════════════════════════════════

def generate_briefing_content(stories: list[dict], date_str: str) -> str:
    """Use LLM to write Gil Gatson's analysis of REAL news stories."""
    if len(stories) < 3:
        log.warning(f"Only {len(stories)} stories found — broadening might be needed")

    # Take top 6 stories (or fewer if not enough)
    top_stories = stories[:6]

    # Build the news digest for the LLM
    news_digest = ""
    for i, s in enumerate(top_stories, 1):
        news_digest += f"{i}. HEADLINE: {s['title']}\n"
        news_digest += f"   SOURCE: {s['source']}\n"
        news_digest += f"   URL: {s['url']}\n\n"

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """You are Gil Gatson, a contrarian geopolitical analyst specializing in AI, semiconductors, and the US-China tech war.

BRAND VOICE:
- Contrarian and provocative
- Skeptical of mainstream narratives
- Data-driven and hard-hitting
- No fluff, no cope, just hard truths
- Target audience: Investors, policy makers, tech leaders

CRITICAL RULES:
- You are given REAL news headlines with REAL URLs. Use them EXACTLY as provided.
- Do NOT invent, fabricate, or modify any URLs or headlines.
- Each bullet point MUST use the exact headline and URL provided.

WRITING STYLE:
- 400-500 words total
- One bullet point per story (up to 6 stories)
- Each bullet starts with: **[Exact Headline](exact_url)**
- Follow with 2-3 sentences of sharp, contrarian analysis
- Challenge conventional wisdom
- Point out hidden risks, contradictions, or geopolitical implications
- End with: "---\\n\\n*Sources: Hacker News, Techmeme, AP News, Ars Technica | Compiled [Date]*"

NO hashtags, NO calls-to-action, NO promotional language.
Focus on exposing uncomfortable truths that mainstream coverage misses.""",
            },
            {
                "role": "user",
                "content": f"""Write a daily tech briefing for {date_str} based on these REAL news stories.
Use the EXACT headlines and URLs provided below. Do NOT change or fabricate any URLs.

NEWS STORIES:
{news_digest}

Remember: contrarian analysis that challenges mainstream narratives. Each story should reveal hidden risks or contradictions.""",
            },
        ],
        temperature=0.8,
        max_tokens=1500,
    )

    return response.choices[0].message.content


def generate_seo_metadata(stories: list[dict]) -> dict:
    """Generate unique SEO metadata from the actual stories."""
    # Build a description from actual headlines
    top_titles = [s["title"][:60] for s in stories[:3]]
    topics_str = "; ".join(top_titles)

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """Generate SEO metadata based on these real news headlines.
Return ONLY valid JSON with these fields:
- "description": A unique, specific meta description (150-160 chars) mentioning key topics from today's stories
- "keywords": Array of 5-8 relevant keywords extracted from the headlines
- "topics": One-sentence summary of main topics covered

The description MUST be unique and specific to these stories. Do NOT use generic descriptions.""",
            },
            {
                "role": "user",
                "content": f"Headlines:\n{topics_str}",
            },
        ],
        temperature=0.3,
        max_tokens=300,
    )

    raw = response.choices[0].message.content.strip()
    # Try to extract JSON from the response
    try:
        # Handle markdown code blocks
        if "```" in raw:
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
            if match:
                raw = match.group(1)
        return json.loads(raw)
    except json.JSONDecodeError:
        log.warning("Failed to parse SEO metadata JSON, using fallback")
        # Fallback: build from actual headlines
        return {
            "description": f"Today's briefing covers {top_titles[0][:50]} and more key developments in AI and semiconductors.",
            "keywords": ["AI", "semiconductors", "tech war", "geopolitics"],
            "topics": topics_str[:150],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FILE OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

def save_briefing(content: str, metadata: dict, date_str: str, formatted_date: str) -> str:
    """Save the briefing as a Markdown file with proper frontmatter."""
    filename = f"daily-briefing-{date_str}.md"
    filepath = os.path.join(BLOG_DIR, filename)

    description = metadata.get("description", "")
    keywords = metadata.get("keywords", [])
    topics = metadata.get("topics", "")

    frontmatter = f"""---
layout: ../../layouts/BlogPostLayout.astro
title: "Daily Tech Briefing - {formatted_date}"
description: "{description}"
pubDate: "{formatted_date}"
author: "Gil Gatson"
keywords: {json.dumps(keywords)}
topics: "{topics}"
---

"""
    with open(filepath, "w") as f:
        f.write(frontmatter + content)

    log.info(f"Saved briefing to {filepath}")
    log.info(f"SEO Description: {description}")
    return filepath


def git_commit_and_push(date_str: str):
    """Commit and push changes to GitHub."""
    os.chdir(REPO_DIR)
    os.system("git add .")
    os.system(f'git commit -m "Add daily briefing for {date_str} (real news)"')
    os.system("git push origin main")
    log.info("Changes pushed to GitHub")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main(target_date: str = None):
    """Main execution flow.

    Args:
        target_date: Optional date string in YYYY-MM-DD format.
                     If None, uses today's date.
    """
    log.info("=" * 60)
    log.info("Gil Gatson Daily Tech Briefing Generator (Live News)")
    log.info("=" * 60)

    # Determine date
    if target_date:
        now = datetime.strptime(target_date, "%Y-%m-%d")
    else:
        now = datetime.now()

    date_str = now.strftime("%Y-%m-%d")
    formatted_date = now.strftime("%B %d, %Y")

    log.info(f"Generating briefing for {formatted_date}")

    # Step 1: Fetch real news
    log.info("Step 1: Fetching real news from live sources...")
    stories = fetch_all_news()

    if not stories:
        log.error("FATAL: No stories fetched from any source. Aborting.")
        sys.exit(1)

    if len(stories) < 3:
        log.warning(f"Only {len(stories)} stories found. Briefing may be thin.")

    # Log what we found
    log.info("Top stories for today's briefing:")
    for i, s in enumerate(stories[:6], 1):
        log.info(f"  {i}. [{s['source']}] {s['title'][:80]}")

    # Step 2: Generate SEO metadata from real headlines
    log.info("Step 2: Generating SEO metadata...")
    metadata = generate_seo_metadata(stories)

    # Step 3: Generate Gil's analysis of the real news
    log.info("Step 3: Generating Gil Gatson's analysis...")
    content = generate_briefing_content(stories, formatted_date)

    # Step 4: Save
    log.info("Step 4: Saving briefing...")
    filepath = save_briefing(content, metadata, date_str, formatted_date)

    # Step 5: Git commit and push
    log.info("Step 5: Committing and pushing to GitHub...")
    git_commit_and_push(date_str)

    log.info("=" * 60)
    log.info("Daily briefing published successfully!")
    log.info(f"View at: https://gilgatson.com/blog/daily-briefing-{date_str}")
    log.info("=" * 60)

    return filepath


if __name__ == "__main__":
    # Accept optional date argument: python generate_daily_briefing_enhanced.py 2026-02-09
    target = sys.argv[1] if len(sys.argv) > 1 else None
    main(target_date=target)
