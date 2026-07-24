from pathlib import Path

from src.models.articles import CollectedArticle, ExtractedArticle, ProcessedArticle, RetrievedArticle
from src.utils import jsonl_file_manager as file_manager


class ArticleRepository:

    def load_collected_articles(
        self,
        collected_articles_file: Path
    ) -> list[CollectedArticle]:

        records = file_manager.load_jsonl_file(
            collected_articles_file
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
        collected_articles_file: Path
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

        file_manager.save_to_jsonl_file(
            collected_articles_file,
            records,
        )

    def load_extracted_articles(
        self,
        extracted_articles_file: Path
    ) -> list[ExtractedArticle]:

        records = file_manager.load_jsonl_file(
            extracted_articles_file
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
        extracted_articles_file: Path
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

        file_manager.append_to_jsonl_file(
            extracted_articles_file,
            records,
        )

    def remove_extracted_articles(
        self,
        extracted_articles: list[ExtractedArticle],
        extracted_articles_file: Path
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

        file_manager.save_to_jsonl_file(
            extracted_articles_file,
            remaining_articles,
        )
    
    def load_processed_articles(
        self,
        processed_articles_file: Path
    ) -> list[ProcessedArticle]:

        records = file_manager.load_jsonl_file(
            processed_articles_file
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
        processed_articles_file: Path
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

        file_manager.save_to_jsonl_file(
            processed_articles_file,
            records,
        )

    def remove_processed_articles(
        self,
        processed_articles: list[ProcessedArticle],
        processed_articles_file: Path
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

        file_manager.save_to_jsonl_file(
            processed_articles_file,
            remaining_articles,
        )

    def load_retrieved_articles(
        self,
        retrieved_articles_file: Path
    ) -> list[RetrievedArticle]:

        records = file_manager.load_jsonl_file(
            retrieved_articles_file
        )

        return [
            RetrievedArticle(
                title=record["title"],
                source=record["source"],
                link=record["link"],
                published=record["published"],
                profile_id=record["profile_id"],
                lexical_score=record["lexical_score"],
                detected_language=record["detected_language"]
            )
            for record in records
        ]
    
    def save_retrieved_articles(
        self,
        retrieved_articles: list[RetrievedArticle],
        retrieved_articles_file: Path
    ) -> None:

        records = [
            {
                "title": article.title,
                "source": article.source,
                "link": article.link,
                "published": article.published,
                "profile_id": article.profile_id,
                "lexical_score": article.lexical_score,
                "detected_language": article.detected_language
            }
            for article in retrieved_articles
        ]

        file_manager.save_to_jsonl_file(
            retrieved_articles_file,
            records,
        )