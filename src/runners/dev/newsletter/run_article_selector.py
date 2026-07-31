"""
Development runner for testing article selection.
"""

from src.models.articles import CandidateArticle
from src.repositories.article_repository import ArticleRepository
from src.repositories.profile_repository import ProfileRepository
from src.services.article_processor.article_selector import select_candidate_articles

from src.config.config_loader import load_article_processor_config, load_newsletter_config


def main() -> None:
    """
    Select the best candidate articles for every user profile.
    """
    article_processor_config = load_article_processor_config()
    newsletter_config = load_newsletter_config()

    article_repo = ArticleRepository()
    profile_repo = ProfileRepository()

    retrieved_articles = article_repo.load_articles(
        articles_file= newsletter_config.retrieved_articles_file,
        article_type= CandidateArticle
    )
    profiles = profile_repo.load_newsletter_profiles(
        newsletter_profiles_file= newsletter_config.newsletter_profiles
    )

    articles_by_profile: dict[int, list[CandidateArticle]] = {}
    for article in retrieved_articles:
        articles_by_profile.setdefault(
            article.profile_id,
            []
        ).append(article)

    all_selected_articles: list[CandidateArticle] = []
    try:
        for profile in profiles:
            candidate_limit = (
                profile.max_articles_included
                + article_processor_config.selection_margin
            )

            profile_articles = articles_by_profile.get(
                profile.profile_id,
                []
            )

            selected_articles = select_candidate_articles(
                candidates= profile_articles,
                max_articles= candidate_limit
            )

            all_selected_articles.extend(selected_articles)
    except KeyboardInterrupt:
            print("\nExecution interrupted by user.")
    finally:        
        article_repo.save_articles(
            articles= all_selected_articles,
            articles_file= article_processor_config.selected_articles_file
        )


if __name__ == "__main__":
    main()