"""
This script collects and parses RSS feeds from a list of URLs provided in a text 
file. It extracts the latest articles from each feed, cleans the HTML content 
in the summaries, and saves the parsed articles to a JSONL file.
"""

import feedparser
from datetime import timedelta
from pathlib import Path
from src.models.articles import CollectedArticle

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

# -------------------------
# RSS parsing
# -------------------------

def _parse_feed(feed_url: str, max_articles_per_feed: int) -> list[CollectedArticle]:
    feed = feedparser.parse(feed_url)
    articles: list[CollectedArticle] = []

    for entry in feed.entries[:max_articles_per_feed]:
        published_dt = parse_datetime(entry.get("published") or entry.get("updated"))

        article = CollectedArticle(
            title= entry.get("title", ""),
            source= feed_url,
            link= entry.get("link", ""),
            published= (
                datetime_to_iso(published_dt)
                if published_dt
                else None
            ),
        )

        articles.append(article)

    return articles


# -------------------------
# Core pipeline
# -------------------------

def collect_from_rss_feeds(
    existing_articles: list[CollectedArticle],
    feed_urls_file: str | Path,
    max_articles_per_feed: int,
    collection_window_days: int,
) -> list[CollectedArticle]:
    """
    Collect articles from RSS feeds and update the local article collection.

    Existing articles whose publication date falls outside the retention
    period are discarded. Newly collected articles are also filtered using the
    same retention policy before being added to the collection. Duplicate
    articles are identified by their URL and ignored.

    Args:
        feed_urls_file:
            Path to the file containing the RSS feed URLs.

        max_articles_per_feed:
            Maximum number of articles to retrieve from each RSS feed.

        collection_window_days:
            Number of days to retain articles in the collection. Articles older
            than this window will be discarded.
    """

    feed_urls = _load_feed_urls(feed_urls_file)

    # Compute cutoff
    cutoff = utc_now() - timedelta(days=collection_window_days)

    # Filter existing articles
    seen_links: set[str] = set()
    filtered_articles: list[CollectedArticle] = []

    for article in existing_articles:
        seen_links.add(article.link)

        published = parse_datetime(article.published)

        if published is not None and published >= cutoff:
            filtered_articles.append(article)

    # Fetch and filter new articles
    new_articles: list[CollectedArticle] = []

    for url in feed_urls:
        articles = _parse_feed(url, max_articles_per_feed)

        for article in articles:

            link = article.link

            if not link or link in seen_links:
                continue

            published = parse_datetime(article.published)

            if published is not None and published >= cutoff:
                new_articles.append(article)
                seen_links.add(link)

    # Merge old and new articles
    final_articles = filtered_articles + new_articles

    return final_articles