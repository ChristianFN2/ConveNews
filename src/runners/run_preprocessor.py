"""
Entry point for the preprocessing process.

This script loads the preprocessing configuratio 
and executes the complete preprocessing process.
"""

from src.config.config_loader import load_preprocessor_config
from src.services.preprocessor.main_preprocessor import apply_preprocessing
from src.repositories.article_repository import ArticleRepository


def main() -> None:
    """
    Load the preprocessing configuration and execute the preprocessing
    pipeline.
    """
    config = load_preprocessor_config()

    repo = ArticleRepository(
        extracted_articles_file=(
            config.input_articles_file
        ),
        processed_articles_file=(
            config.processed_articles_file
        )
    )

    all_extracted_articles = repo.load_extracted_articles()
    prev_processed_articles = repo.load_processed_articles()

    processed_links = {
        article.link
        for article in prev_processed_articles
    }

    to_process_articles = [
        article
        for article in all_extracted_articles
        if article.link not in processed_links
    ]

    final_preprocessed_articles = prev_processed_articles.extend(
        apply_preprocessing(
            to_process_articles,
            config.text_processing
        )
    )

    repo.save_processed_articles(final_preprocessed_articles)


if __name__ == "__main__":
    main()