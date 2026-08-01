from pathlib import Path
from typing import TypeVar

from src.models.articles import Article
from src.utils import jsonl_file_manager as file_manager


ArticleType = TypeVar("ArticleType", bound=Article)


class ArticleRepository:
    """
    Repository responsible for persisting article entities.

    All article types must inherit from Article and be serializable
    to and from JSON-compatible dictionaries.
    """

    def load_articles(
        self,
        articles_file: Path,
        article_type: type[ArticleType],
    ) -> list[ArticleType]:
        """
        Load articles from a JSONL file.

        Args:
            articles_file: JSONL file containing the articles.
            article_type: Concrete article type to instantiate.

        Returns:
            A list of loaded articles.
        """
        records = file_manager.load_jsonl_file(
            articles_file
        )

        if(len(records)==0):
            return []


        return [
            article_type(**record)
            for record in records
        ]

    def save_articles(
        self,
        articles_file: Path,
        articles: list[ArticleType],
    ) -> None:
        """
        Overwrite a JSONL file with the provided articles.

        Args:
            articles_file: Destination file.
            articles: Articles to persist.
        """
        records = [
            vars(article)
            for article in articles
        ]

        file_manager.save_to_jsonl_file(
            articles_file,
            records,
        )

    def append_articles(
        self,
        articles_file: Path,
        articles: list[ArticleType],
    ) -> None:
        """
        Append articles to an existing JSONL file.

        Args:
            articles_file: Destination file.
            articles: Articles to append.
        """
        records = [
            vars(article)
            for article in articles
        ]

        file_manager.append_to_jsonl_file(
            articles_file,
            records,
        )

    def remove_articles(
        self,
        articles_file: Path,
        articles_to_remove: list[ArticleType],
    ) -> None:
        """
        Remove articles matching the links of the provided articles.

        Args:
            articles_file: Source file.
            articles_to_remove: Articles whose links should be removed.
        """
        existing_records = file_manager.load_jsonl_file(
            articles_file
        )

        links_to_remove = {
            article.link
            for article in articles_to_remove
        }

        filtered_records = [
            record
            for record in existing_records
            if record["link"] not in links_to_remove
        ]

        file_manager.save_to_jsonl_file(
            articles_file,
            filtered_records,
        )