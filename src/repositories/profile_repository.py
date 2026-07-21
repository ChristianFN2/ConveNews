from pathlib import Path

from src.models.profiles import NewsletterProfile
from src.utils import jsonl_file_manager as file_manager


class ProfileRepository:

    def __init__(
        self,
        newsletter_profiles_file: Path,
    ):
        self.newsletter_profiles_file = (
            newsletter_profiles_file
        )

    def load_newsletter_profiles(
        self,
    ) -> list[NewsletterProfile]:

        records = file_manager.load_jsonl_file(
            self.newsletter_profiles_file
        )

        return [
            NewsletterProfile(
                profile_id= record["profile_id"],
                user_id= record["user_id"],
                profile_title= record["profile_title"],
                interest_description= record["interest_description"],
                selected_keywords= record["selected_keywords"],
                target_language= record["target_language"],
                max_articles_included= record["max_articles_included"],
                included_sources= record["included_sources"],
                covered_period_days= record["covered_period_days"],
                reading_time_minutes= record["reading_time_minutes"],
                is_initialization_pending= record["is_initialization_pending"],
                interest_summary= record["interest_summary"],
                generated_queries= record["generated_queries"]
            )
            for record in records
        ]
    
    def save_newsletter_profiles(
        self,
        newsletter_profiles: list[NewsletterProfile],
    ) -> None:

        records = [
            {
                "profile_id": article.profile_id,
                "user_id": article.user_id,
                "profile_title": article.profile_title,
                "interest_description": article.interest_description,
                "selected_keywords": article.selected_keywords,
                "target_language": article.target_language,
                "max_articles_included": article.max_articles_included,
                "included_sources": article.included_sources,
                "covered_period_days": article.covered_period_days,
                "reading_time_minutes": article.reading_time_minutes,
                "is_initialization_pending": article.is_initialization_pending,
                "interest_summary": article.interest_summary,
                "generated_queries": article.generated_queries
            }
            for article in newsletter_profiles
        ]

        file_manager.save_to_jsonl_file(
            self.newsletter_profiles_file,
            records,
        )