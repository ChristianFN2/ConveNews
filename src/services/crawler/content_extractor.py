"""
Extracts content from articles listed in a JSONL file and saves the
extracted content to another JSONL file.
Also generates per-source statistics in JSONL format.
"""

from src.models.articles import Article, ExtractedArticle

import requests
import trafilatura


def _download_articles(
    articles_to_download: list[Article]
):
    """
    Download and extract content for articles

    Returns:
        downloaded articles
    """
    extracted_articles = []

    for article in articles_to_download:

        try:
            response = requests.get(article.link, timeout=10)

            extracted = trafilatura.extract(response.text)

            extracted_article = ExtractedArticle(
                title=article.title,
                source=article.source,
                link=article.link,
                published=article.published,
                content=extracted
            )
            extracted_articles.append(extracted_article)

        except Exception:
            continue

    return extracted_articles


def extract_content_from_articles(
    articles_to_extract: list[Article]
) -> list[ExtractedArticle]:
    """
    Extract content from articles

    Args:
        articles_to_extract:
            articles containing the links whose content will be extracted

        stats_file:
            JSONL file where extraction statistics are written.
    """

    downloaded_articles = _download_articles(
        articles_to_extract
    )

    return downloaded_articles