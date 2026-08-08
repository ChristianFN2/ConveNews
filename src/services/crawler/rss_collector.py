"""
This script collects and parses RSS feeds from a list of URLs provided in a text 
file. It extracts the latest articles from each feed
"""

import feedparser
from datetime import timedelta
from src.models.articles import Article

from src.utils.datetime_utils import (
    parse_datetime,
    datetime_to_iso,
    utc_now
)


def _parse_feed(feed_url: str) -> list[Article]:
    feed = feedparser.parse(feed_url)
    articles: list[Article] = []

    for entry in feed.entries:
        published_dt = parse_datetime(entry.get("published") or entry.get("updated"))

        article = Article(
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
    feed_urls: list[str],
    collection_window_days: int,
) -> list[Article]:
    """
    Collect articles from RSS feeds

    Args:
        feed_urls:
            List of urls used for the collection

        collection_window_days:
            Articles older than this window will be discarded.
    """

    # Compute cutoff
    cutoff = utc_now() - timedelta(days=collection_window_days)

    # Fetch articles
    collected_articles: list[Article] = []

    for url in feed_urls:
        articles = _parse_feed(url)

        for article in articles:

            published = parse_datetime(article.published)

            if published is not None and published >= cutoff:
                collected_articles.append(article)

    return collected_articles