import json
from pathlib import Path

from src.models.articles import CollectedArticle, ExtractedArticle


class ArticleRepository:

    def __init__(
        self,
        collected_articles_file: Path,
        extracted_articles_file: Path,
    ):
        self.collected_articles_file = (
            collected_articles_file
        )
        self.extracted_articles_file = (
            extracted_articles_file
        )

    def load_collected_articles(
        self,
    ) -> list[CollectedArticle]:

        records = self._load_jsonl_file(
            self.collected_articles_file
        )

        return [
            CollectedArticle(
                title=record["title"],
                source=record["source"],
                link=record["link"],
                published=record["published"],
            )
            for record in records
        ]

    def save_collected_articles(
        self,
        collected_articles: list[CollectedArticle],
    ) -> None:

        records = [
            {
                "title": article.title,
                "source": article.source,
                "link": article.link,
                "published": article.published,
            }
            for article in collected_articles
        ]

        self._save_jsonl_file(
            self.collected_articles_file,
            records,
        )

    
    def save_extracted_articles(
        self,
        extracted_articles: list[ExtractedArticle],
    ) -> None:

        records = [
            {
                "title": article.title,
                "source": article.source,
                "link": article.link,
                "published": article.published,
                "content": article.content,
            }
            for article in extracted_articles
        ]

        self._save_jsonl_file(
            self.extracted_articles_file,
            records,
        )

    def _load_jsonl_file(
        self,
        file_path: Path,
    ) -> list[dict]:

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return [
                json.loads(line)
                for line in file
            ]
    
    def _save_jsonl_file(
        self,
        file_path: Path,
        records: list[dict],
    ) -> None:

        with file_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            for record in records:
                file.write(
                    json.dumps(
                        record,
                        ensure_ascii=False,
                    )
                )

                file.write("\n")