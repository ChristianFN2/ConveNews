"""
Build HTML newsletters from evaluated articles.
"""

from src.models.articles import EvaluatedArticle
from src.models.newsletters import DeliveryStatus, Newsletter
from src.models.profiles import NewsletterProfile
from src.repositories.article_repository import ArticleRepository
from src.repositories.newsletter_repository import NewsletterRepository
from src.repositories.profile_repository import ProfileRepository
from src.repositories.source_repository import SourceRepository
from src.services.newsletter.templates.localization import LOCALIZATION
from src.utils.datetime_utils import get_current_day

from src.config.config_loader import load_newsletter_config, load_application_config, load_source_config
from src.services.newsletter.newsletter_builder import build_newsletter


def main() -> None:
    """
    Build one newsletter for every user profile.
    """

    newsletter_config = load_newsletter_config()
    app_config = load_application_config()
    source_config = load_source_config()

    article_repo = ArticleRepository()
    profile_repo = ProfileRepository()
    newsletter_repo = NewsletterRepository()
    source_repo = SourceRepository()

    evaluated_articles = article_repo.load_articles(
        articles_file= newsletter_config.evaluated_articles_file,
        article_type= EvaluatedArticle
    )
    profiles = profile_repo.load_newsletter_profiles(
        newsletter_profiles_file= newsletter_config.newsletter_profiles
    )
    sources = source_repo.load_sources(
        sources_file= source_config.sources_file
    )

    articles_by_profile_id: dict[int, list[EvaluatedArticle]] = {}
    for article in evaluated_articles:
        articles_by_profile_id.setdefault(
            article.profile_id,
            []
        ).append(article)

    profiles_by_id: dict[int, NewsletterProfile] = {
        profile.profile_id: profile
        for profile in profiles
    }

    sources_by_link = {
        source.link: source
        for source in sources
    }

    last_newsletter_id = newsletter_repo.get_last_id(
        newsletters_file= newsletter_config.newsletters_file
    )

    built_newsletters: list[Newsletter] = {}
    for profile_id in articles_by_profile_id:

        profile_articles = articles_by_profile_id.get(profile_id)
        newsletter_profile = profiles_by_id.get(profile_id)

        final_profile_articles = _get_final_articles(
            profile_articles,
            newsletter_config.relevance_threshold,
            newsletter_profile.max_articles_included
        )

        generation_date = get_current_day()

        newsletter_content = build_newsletter(
            articles= final_profile_articles,
            profile= newsletter_profile,
            newsletter_template= newsletter_config.newsletter_template,
            article_template= newsletter_config.article_template,
            sources_by_link= sources_by_link,
            localization= LOCALIZATION[newsletter_profile.target_language],
            site_url= app_config.site_url,
            about_url= app_config.about_url,
            generation_date= generation_date
        )

        last_newsletter_id += 1
        built_newsletters.append(Newsletter(
            newsletter_id= last_newsletter_id,
            profile_id= newsletter_profile.profile_id,
            generated_at= generation_date,
            content= newsletter_content,
            delivery_status= DeliveryStatus.PENDING
        ))

    newsletter_repo.append_newsletters(built_newsletters)


def _get_final_articles(
        profile_articles: list[EvaluatedArticle],
        relevance_threshold: float,
        max_articles_included: int
    ):
    filtered_articles = [
        article
        for article in profile_articles
        if (
            article.relevance_score
            >= relevance_threshold
        )
    ]

    filtered_articles.sort(
        key=lambda article: article.relevance_score,
        reverse=True,
    )

    return filtered_articles[:max_articles_included]


if __name__ == "__main__":
    main()