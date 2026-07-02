"""Collects articles from RSS feeds and then extracts their content"""

from src.crawler.types import CrawlerConfig
from src.crawler import rss_collector, content_extractor



def crawl(config: CrawlerConfig) -> None:
    """
    Execute the full RSS crawling pipeline.

    This function performs two sequential steps:

    1. Reads RSS feeds from `feed_urls_file` and collects article metadata
       (URLs, titles, publication dates, summaries) into `collected_articles_file`.

    2. Downloads each collected article and extracts its main textual content,
       saving the results into `extracted_articles_file`.

    Args:
        config: The crawler configuration.
    """

    rss_collector.collect_from_rss_feeds(
        config.feed_urls_file,
        config.collected_articles_file,
        config.max_articles_per_feed,
        config.collection_window_days
    )

    content_extractor.extract_content_from_articles(
        config.collected_articles_file,
        config.extracted_articles_file,
        config.stats_file,
        config.state_file,
        config.extraction_retention_days
    )