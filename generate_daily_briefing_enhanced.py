#!/usr/bin/env python3
"""
Enhanced Daily Tech Briefing Generator for gilgatson.com with SEO optimization
Fetches news from Reuters and AP, generates briefing with keyword-rich metadata.
"""

import os
import sys
import json
from datetime import datetime
from openai import OpenAI

def fetch_trending_news():
    """Fetch trending tech news using OpenAI with web search capabilities."""
    client = OpenAI()
    
    today = datetime.now().strftime("%B %d, %Y")
    
    # Use OpenAI to fetch and summarize trending news
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """You are a news aggregator assistant. Your task is to find the top 6 trending tech news stories from the past 24 hours, focusing on:
- AI developments and policy
- Semiconductor industry news
- US-China tech competition
- Geopolitical tech issues

IMPORTANT: Only use news from Reuters (reuters.com) and Associated Press (apnews.com). Do not use any other sources.

For each story, provide:
1. A clear headline
2. The full Reuters or AP URL
3. A 2-3 sentence factual summary
4. 2-3 relevant keywords (e.g., "AI chips", "export controls", "TSMC")

Format your response as a JSON array with objects containing: headline, url, summary, keywords"""
            },
            {
                "role": "user",
                "content": f"Find the top 6 trending tech news stories from Reuters and AP for {today}. Focus on AI, semiconductors, and US-China tech competition."
            }
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

def generate_article_metadata(news_data):
    """Generate SEO-optimized metadata from news data."""
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """You are an SEO expert. Based on the news stories provided, generate:
1. A unique, keyword-rich meta description (150-160 characters) that includes key terms like "AI", "semiconductors", "US-China", specific companies, or policies mentioned
2. A list of 5-8 relevant keywords/tags for the article
3. A brief summary of the main topics (one sentence)

Format as JSON: {"description": "...", "keywords": ["...", "..."], "topics": "..."}"""
            },
            {
                "role": "user",
                "content": f"Generate SEO metadata for these news stories:\n\n{news_data}"
            }
        ],
        temperature=0.5
    )
    
    return response.choices[0].message.content

def generate_article(news_data, date_str):
    """Generate a Gil Gatson style article from news data."""
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

WRITING STYLE:
- 400-500 words total
- 6 bullet points, each covering one news story
- Each bullet starts with a linked headline in bold
- Follow with 2-3 sentences of sharp, contrarian analysis
- Challenge conventional wisdom
- Point out hidden risks, contradictions, or geopolitical implications
- Use numbered references [1], [2], etc.
- End with: "---\n\n*Sources: Reuters, AP | Compiled [Date]*"

NO hashtags, NO calls-to-action, NO promotional language.

Focus on exposing uncomfortable truths that mainstream coverage misses."""
            },
            {
                "role": "user",
                "content": f"Write a daily tech briefing for {date_str} based on this news data:\n\n{news_data}\n\nRemember: contrarian analysis that challenges mainstream narratives. Each story should reveal hidden risks or contradictions."
            }
        ],
        temperature=0.8,
        max_tokens=1500
    )
    
    return response.choices[0].message.content

def save_article(content, metadata, date_str, formatted_date):
    """Save the article to the blog directory with enhanced SEO metadata."""
    # Create filename from date
    filename = f"daily-briefing-{date_str}.md"
    filepath = f"/home/ubuntu/gilgatson-website/src/pages/blog/{filename}"
    
    # Parse metadata
    try:
        meta = json.loads(metadata)
        description = meta.get("description", "Key developments in AI, semiconductors, and the US-China tech war from the past 24 hours.")
        keywords = meta.get("keywords", [])
        topics = meta.get("topics", "AI, semiconductors, US-China tech competition")
    except:
        description = "Key developments in AI, semiconductors, and the US-China tech war from the past 24 hours."
        keywords = ["AI", "semiconductors", "US-China tech war"]
        topics = "AI, semiconductors, US-China tech competition"
    
    # Create frontmatter with enhanced SEO
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
    
    # Write the file
    with open(filepath, 'w') as f:
        f.write(frontmatter + content)
    
    print(f"✓ Article saved to {filepath}")
    print(f"✓ SEO Description: {description}")
    print(f"✓ Keywords: {', '.join(keywords)}")
    return filepath

def git_commit_and_push(filename):
    """Commit and push the new article to GitHub."""
    os.chdir("/home/ubuntu/gilgatson-website")
    
    # Git operations
    os.system("git add .")
    os.system(f'git commit -m "Add daily briefing for {filename}"')
    os.system("git push origin main")
    
    print("✓ Changes pushed to GitHub")
    print("✓ Cloudflare Pages will auto-deploy within 1-2 minutes")

def main():
    """Main execution flow."""
    print("=" * 60)
    print("Gil Gatson Daily Tech Briefing Generator (Enhanced SEO)")
    print("=" * 60)
    
    # Get current date
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    formatted_date = now.strftime("%B %d, %Y")
    
    print(f"\n📅 Generating briefing for {formatted_date}")
    
    # Step 1: Fetch news
    print("\n🔍 Fetching trending news from Reuters and AP...")
    try:
        news_data = fetch_trending_news()
        print("✓ News data retrieved")
    except Exception as e:
        print(f"✗ Error fetching news: {e}")
        sys.exit(1)
    
    # Step 2: Generate SEO metadata
    print("\n🎯 Generating SEO metadata...")
    try:
        metadata = generate_article_metadata(news_data)
        print("✓ SEO metadata generated")
    except Exception as e:
        print(f"⚠ Warning: Could not generate metadata: {e}")
        metadata = '{"description": "Key developments in AI, semiconductors, and the US-China tech war from the past 24 hours.", "keywords": ["AI", "semiconductors", "US-China tech war"], "topics": "AI, semiconductors, US-China tech competition"}'
    
    # Step 3: Generate article
    print("\n✍️  Generating article in Gil Gatson's voice...")
    try:
        article_content = generate_article(news_data, formatted_date)
        print("✓ Article generated")
    except Exception as e:
        print(f"✗ Error generating article: {e}")
        sys.exit(1)
    
    # Step 4: Save article
    print("\n💾 Saving article with SEO enhancements...")
    try:
        filepath = save_article(article_content, metadata, date_str, formatted_date)
    except Exception as e:
        print(f"✗ Error saving article: {e}")
        sys.exit(1)
    
    # Step 5: Git commit and push
    print("\n🚀 Committing and pushing to GitHub...")
    try:
        git_commit_and_push(date_str)
    except Exception as e:
        print(f"✗ Error with git operations: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Daily briefing published successfully!")
    print("=" * 60)
    print(f"\nView at: https://gilgatson.com/blog/daily-briefing-{date_str}")
    print("\n")

if __name__ == "__main__":
    main()
