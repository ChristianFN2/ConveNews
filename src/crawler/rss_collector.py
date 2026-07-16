"""
This script collects and parses RSS feeds from a list of URLs provided in a text 
file. It extracts the latest articles from each feed, cleans the HTML content 
in the summaries, and saves the parsed articles to a JSONL file.
"""

import feedparser
import json
import html
import re
from datetime import timedelta
from pathlib import Path

from src.utils.datetime_utils import (
    parse_datetime,
    datetime_to_iso,
    utc_now
)


# -------------------------
# IO helpers
# -------------------------

def _load_feed_urls(file_path: str | Path) -> list[str]:
    urls: list[str] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if url:
                urls.append(url)
    return urls


def _load_jsonl(file_path: Path) -> list[dict]:
    if not file_path.exists():
        return []

    articles = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                articles.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return articles


def _write_jsonl(file_path: Path, articles: list[dict]) -> None:
    with file_path.open("w", encoding="utf-8") as f:
        for article in articles:
            f.write(json.dumps(article, ensure_ascii=False) + "\n")

# -------------------------
# RSS parsing
# -------------------------

def _parse_feed(feed_url: str, max_articles_per_feed: int) -> list[dict]:
    feed = feedparser.parse(feed_url)
    articles: list[dict] = []

    for entry in feed.entries[:max_articles_per_feed]:
        published_dt = parse_datetime(entry.get("published") or entry.get("updated"))

        article = {
            "title": entry.get("title", ""),
            "source": feed_url,
            "link": entry.get("link", ""),
            "published": (
                datetime_to_iso(published_dt)
                if published_dt
                else None
            ),
        }

        articles.append(article)

    return articles


# -------------------------
# Core pipeline
# -------------------------

def collect_from_rss_feeds(
    feed_urls_file: str | Path,
    collected_articles_file: str | Path,
    max_articles_per_feed: int,
    collection_window_days: int,
) -> None:
    """
    Collect articles from RSS feeds and update the local article collection.

    Existing articles whose publication date falls outside the retention
    period are discarded. Newly collected articles are also filtered using the
    same retention policy before being added to the collection. Duplicate
    articles are identified by their URL and ignored.

    Args:
        feed_urls_file:
            Path to the file containing the RSS feed URLs.

        collected_articles_file:
            JSONL file where collected articles are stored.

        max_articles_per_feed:
            Maximum number of articles to retrieve from each RSS feed.

        collection_window_days:
            Number of days to retain articles in the collection. Articles older
            than this window will be discarded.
    """

    feed_urls = _load_feed_urls(feed_urls_file)
    collected_articles_file = Path(collected_articles_file)

    # 1. Load existing articles
    existing_articles = _load_jsonl(collected_articles_file)

    # 2. Compute cutoff
    cutoff = utc_now() - timedelta(days=collection_window_days)

    # 3. Filter existing articles
    seen_links: set[str] = set()
    filtered_articles: list[dict] = []

    for article in existing_articles:
        seen_links.add(article.get("link"))

        published = parse_datetime(article.get("published"))

        if published is not None and published >= cutoff:
            filtered_articles.append(article)

    # 4. Fetch and filter new articles
    new_articles: list[dict] = []

    for url in feed_urls:
        articles = _parse_feed(url, max_articles_per_feed)

        for article in articles:

            link = article.get("link")

            if not link or link in seen_links:
                continue

            published = parse_datetime(article.get("published"))

            if published is not None and published >= cutoff:
                new_articles.append(article)
                seen_links.add(link)

    # 5. Merge old and new articles
    final_articles = filtered_articles + new_articles

    # 6. Replace the collection atomically
    temp_file = collected_articles_file.with_suffix(".tmp")
    _write_jsonl(temp_file, final_articles)
    temp_file.replace(collected_articles_file)