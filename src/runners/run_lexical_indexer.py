"""
Entry point for the lexical indexing process.

This script loads the indexing configuration 
and executes the complete indexing process.
"""

from src.config.config_loader import load_lexical_indexer_config
from src.services.lexical_indexer import main_indexer
from src.repositories.article_repository import ArticleRepository


def main() -> None:
    """
    Load the indexing configuration and execute the indexing
    pipeline.
    """
    config = load_lexical_indexer_config()
    repo = ArticleRepository(
        processed_articles_file=config.input_articles_file
    )

    processed_articles = repo.load_processed_articles()

    main_indexer.update_index(
        processed_articles,
        config.index_dir
    )


if __name__ == "__main__":
    main()