"""
Entry point for the crawling pipeline.

This script loads the crawler configuration
file and executes the complete crawling pipeline.
"""

from src.config.types.crawler import CrawlerConfig
from src.config.types.sources import SourceConfig
from src.models.articles import Article, ExtractedArticle
from src.config.config_loader import load_crawler_config
from src.config.config_loader import load_source_config
from src.services.crawler import rss_collector, content_extractor, extracted_articles_cleaner
from src.repositories.article_repository import ArticleRepository
from src.repositories.source_repository import SourceRepository

   
def main() -> None:
    crawler_config = load_crawler_config()
    source_config = load_source_config()

    article_repo = ArticleRepository()
    source_repo = SourceRepository()

    _run_collector(
        article_repo= article_repo,
        source_repo= source_repo,
        crawler_config= crawler_config,
        source_config= source_config
    )

    _run_extractor(
        article_repo= article_repo,
        crawler_config= crawler_config
    )

def _run_collector(
    article_repo: ArticleRepository,
    source_repo: SourceRepository,
    crawler_config: CrawlerConfig,
    source_config: SourceConfig,
) -> None:
    feed_urls = [
        source.link
        for source in source_repo.load_sources(
            sources_file=source_config.sources_file,
        )
    ]

    all_collected_articles = (
        rss_collector.collect_from_rss_feeds(
            feed_urls=feed_urls,
            collection_window_days=(
                crawler_config.collection_window_days
            ),
        )
    )

    article_repo.save_articles(
        articles=all_collected_articles,
        articles_file=crawler_config.collected_articles_file,
    )

def _run_extractor(
    article_repo: ArticleRepository,
    crawler_config: CrawlerConfig,
) -> None:
    prev_extracted_articles = article_repo.load_articles(
        article_type=ExtractedArticle,
        articles_file=crawler_config.extracted_articles_file,
    )

    expired_articles = (
        extracted_articles_cleaner.get_expired_articles(
            prev_extracted_articles,
            crawler_config.extraction_retention_days,
        )
    )

    article_repo.remove_articles(
        articles_to_remove=expired_articles,
        articles_file=crawler_config.extracted_articles_file,
    )

    expired_links = {
        article.link
        for article in expired_articles
    }

    current_extracted_articles = [
        article
        for article in prev_extracted_articles
        if article.link not in expired_links
    ]

    collected_articles = article_repo.load_articles(
        article_type=Article,
        articles_file=crawler_config.collected_articles_file,
    )

    articles_to_extract, articles_to_remove = (
        _update_extracted_articles(
            current_extracted_articles=current_extracted_articles,
            new_collected_articles=collected_articles,
            max_articles_per_feed=(
                crawler_config.max_articles_per_feed
            ),
        )
    )

    article_repo.remove_articles(
        articles_to_remove=articles_to_remove,
        articles_file=crawler_config.extracted_articles_file,
    )

    new_extracted_articles = (
        content_extractor.extract_content_from_articles(
            articles_to_extract,
        )
    )

    article_repo.append_articles(
        articles=new_extracted_articles,
        articles_file=crawler_config.extracted_articles_file,
    )

def _update_extracted_articles(
    current_extracted_articles: list[ExtractedArticle],
    new_collected_articles: list[Article],
    max_articles_per_feed: int,
) -> tuple[list[Article], list[ExtractedArticle]]:
    """
    Determine which collected articles should be extracted and which
    previously extracted articles should be removed.

    For each source, only the most recent 'max_articles_per_feed'
    articles are retained.
    """

    existing_links = {
        article.link
        for article in current_extracted_articles
    }

    articles_by_source: dict[str, list[Article]] = {}

    for article in current_extracted_articles:
        articles_by_source.setdefault(
            article.source,
            []
        ).append(article)

    for article in new_collected_articles:
        if article.link not in existing_links:
            articles_by_source.setdefault(
                article.source,
                []
            ).append(article)

    selected_articles: list[Article] = []

    for source_articles in articles_by_source.values():
        source_articles.sort(
            key=lambda article: article.published,
            reverse=True,
        )

        selected_articles.extend(
            source_articles[:max_articles_per_feed]
        )

    selected_links = {
        article.link
        for article in selected_articles
    }

    articles_to_extract = [
        article
        for article in selected_articles
        if article.link not in existing_links
    ]

    articles_to_remove = [
        article
        for article in current_extracted_articles
        if article.link not in selected_links
    ]

    return articles_to_extract, articles_to_remove


if __name__ == "__main__":
    main()