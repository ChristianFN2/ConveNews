"""
Entry point for the preprocessing process.

This script loads the preprocessing configuratio 
and executes the complete preprocessing process.
"""

from src.models.articles import ExtractedArticle, ProcessedArticle
from src.config.config_loader import load_preprocessor_config
from src.services.preprocessor.main_preprocessor import apply_preprocessing
from src.repositories.article_repository import ArticleRepository


def main() -> None:
    """
    Load the preprocessing configuration and execute the preprocessing
    pipeline.
    """
    preprocessor_config = load_preprocessor_config()

    article_repo = ArticleRepository()

    all_extracted_articles = article_repo.load_articles(
        articles_file= preprocessor_config.input_articles_file,
        article_type= ExtractedArticle
    )
    prev_processed_articles = article_repo.load_articles(
        articles_file= preprocessor_config.processed_articles_file,
        article_type= ProcessedArticle
    )

    processed_links = {
        article.link
        for article in prev_processed_articles
    }

    to_process_articles = [
        article
        for article in all_extracted_articles
        if article.link not in processed_links
    ]

    prev_processed_articles.extend(
        apply_preprocessing(
            to_process_articles,
            preprocessor_config.text_processing
        )
    )

    final_preprocessed_articles = prev_processed_articles

    article_repo.save_articles(
        articles= final_preprocessed_articles,
        articles_file= preprocessor_config.processed_articles_file
    )


if __name__ == "__main__":
    main()