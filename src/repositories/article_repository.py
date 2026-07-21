import json
from pathlib import Path

from src.models.articles import CollectedArticle, ExtractedArticle, ProcessedArticle


class ArticleRepository:

    def __init__(
        self,
        collected_articles_file: Path,
        extracted_articles_file: Path,
        processed_articles_file: Path
    ):
        self.collected_articles_file = (
            collected_articles_file
        )
        self.extracted_articles_file = (
            extracted_articles_file
        )
        self.processed_articles_file = (
            processed_articles_file
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

        self._save_to_jsonl_file(
            self.collected_articles_file,
            records,
        )

    def load_extracted_articles(
        self,
    ) -> list[ExtractedArticle]:

        records = self._load_jsonl_file(
            self.extracted_articles_file
        )

        return [
            ExtractedArticle(
                title=record["title"],
                source=record["source"],
                link=record["link"],
                published=record["published"],
                content=record["content"]
            )
            for record in records
        ]
    
    def append_extracted_articles(
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

        self._append_to_jsonl_file(
            self.extracted_articles_file,
            records,
        )

    def remove_extracted_articles(
        self,
        extracted_articles: list[ExtractedArticle]
    ) -> None:
        removed_links = {
            article.link
            for article in extracted_articles
        }

        remaining_articles = [
            article
            for article in self.load_extracted_articles()
            if article.link not in removed_links
        ]

        self._save_jsonl(
            self.extracted_articles_file,
            remaining_articles,
        )
    
    def load_processed_articles(
        self,
    ) -> list[ProcessedArticle]:

        records = self._load_jsonl_file(
            self.processed_articles_file
        )

        return [
            ProcessedArticle(
                title=record["title"],
                source=record["source"],
                link=record["link"],
                published=record["published"],
                processed_content=record["processed_content"],
                processed_title=record["processed_title"],
                detected_language=record["detected_language"]
            )
            for record in records
        ]
    
    def save_processed_articles(
        self,
        processed_articles: list[ProcessedArticle],
    ) -> None:

        records = [
            {
                "title": article.title,
                "source": article.source,
                "link": article.link,
                "published": article.published,
                "content": article.content,
                "processed_content": article.processed_content,
                "processed_title": article.processed_title,
                "detected_language": article.detected_language
            }
            for article in processed_articles
        ]

        self._save_to_jsonl_file(
            self.processed_articles_file,
            records,
        )

    def remove_processed_articles(
        self,
        processed_articles: list[ProcessedArticle]
    ) -> None:
        removed_links = {
            article.link
            for article in processed_articles
        }

        remaining_articles = [
            article
            for article in self.load_processed_articles()
            if article.link not in removed_links
        ]

        self._save_jsonl(
            self.processed_articles_file,
            remaining_articles,
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
    
    def _save_to_jsonl_file(
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
    
    def _append_to_jsonl_file(
        self,
        file_path: Path,
        records: list[dict],
    ) -> None:

        with file_path.open(
            "a",
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