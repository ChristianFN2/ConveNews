"""
Development runner for testing article relevance evaluation.
"""

from src.models.articles import EvaluatedArticle, ExtractedArticle, CandidateArticle
from src.repositories.article_repository import ArticleRepository
from src.repositories.profile_repository import ProfileRepository
from src.llm.client_provider import create_llm_client
from src.config.config_loader import load_llm_config, load_article_processor_config, load_newsletter_config, load_crawler_config
from src.services.llm.relevance_evaluator import evaluate_relevance


def main() -> None:
    """
    Evaluate the relevance of the selected articles for every user
    profile and generate concise summaries.
    """
    llm_config = load_llm_config()
    article_processor_config = load_article_processor_config()
    newsletter_config = load_newsletter_config()
    crawler_config = load_crawler_config()

    profile_repo = ProfileRepository()
    article_repo = ArticleRepository()

    profiles = profile_repo.load_newsletter_profiles(
        newsletter_profiles_file= newsletter_config.newsletter_profiles
    )
    selected_articles = article_repo.load_articles(
        articles_file= article_processor_config.selected_articles_file,
        article_type= CandidateArticle
    )
    extracted_articles = article_repo.load_articles(
        articles_file= crawler_config.extracted_articles_file,
        article_type= ExtractedArticle
    )
    extracted_by_link = {
        article.link: article
        for article in extracted_articles
    }

    articles_by_profile: dict[int, list[CandidateArticle]] = {}
    for article in selected_articles:
        articles_by_profile.setdefault(
            article.profile_id,
            []
        ).append(article)


    evaluated_articles: list[EvaluatedArticle] = []
    client = create_llm_client(llm_config)
    prompt = llm_config.prompts.relevance_evaluation.read_text(
        encoding="utf-8"
    )

    try:
        for profile in profiles:
            profile_articles = articles_by_profile.get(profile.profile_id)

            for article in profile_articles:
                generated_summary_words = _minutes_to_words(
                    reading_time_minutes= profile.reading_time_minutes / profile.max_articles_included,
                    average_reading_speed_wpm= newsletter_config.average_reading_speed_wpm
                )
                evaluated_article = evaluate_relevance(
                    candidate_article= article,
                    article_content= extracted_by_link.get(article.link).content,
                    interest_summary= profile.interest_summary,
                    target_language= profile.target_language,
                    generated_summary_words=generated_summary_words,
                    client= client,
                    prompt= prompt
                )
                evaluated_articles.append(evaluated_article)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
    finally:
        article_repo.save_articles(
            articles_file= newsletter_config.evaluated_articles_file,
            articles= evaluated_articles
        )

def _minutes_to_words(
    reading_time_minutes: float,
    average_reading_speed_wpm: int,
) -> int:
    return round(
        reading_time_minutes
        * average_reading_speed_wpm
    )


if __name__ == "__main__":
    main()