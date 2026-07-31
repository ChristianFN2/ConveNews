"""
Entry point for the lexical indexing process.

This script loads the indexing configuration 
and executes the complete indexing process.
"""

from src.models.articles import ProcessedArticle
from src.config.config_loader import load_lexical_indexer_config
from src.services.lexical_indexer import main_indexer
from src.repositories.article_repository import ArticleRepository


def main() -> None:
    """
    Load the indexing configuration and execute the indexing
    pipeline.
    """
    lex_indexer_config = load_lexical_indexer_config()
    article_repo = ArticleRepository()

    processed_articles = article_repo.load_articles(
        articles_file= lex_indexer_config.input_articles_file,
        article_type= ProcessedArticle
    )

    main_indexer.update_index(
        processed_articles,
        lex_indexer_config.index_dir
    )


if __name__ == "__main__":
    main()