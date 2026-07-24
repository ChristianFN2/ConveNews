"""
Development runner for testing lexical query retrieval.
"""

from src.config.config_loader import load_lexical_indexer_config, load_preprocessor_config, load_newsletter_config
from src.services.lexical_indexer.searcher import search
from src.services.preprocessor.main_preprocessor import process_query
from src.repositories.profile_repository import ProfileRepository
from src.repositories.article_repository import ArticleRepository


def main() -> None:
    """
    Execute all generated lexical queries against the lexical index.
    """
    lexical_indexer_config = load_lexical_indexer_config()
    preprocessor_config = load_preprocessor_config()
    newsletter_config = load_newsletter_config()

    article_repo = ArticleRepository()
    profile_repo = ProfileRepository()

    profiles = profile_repo.load_newsletter_profiles(
        newsletter_profiles_file= newsletter_config.newsletter_profiles
    )

    all_retrieved_articles = []
    try:
        for profile in profiles:
            for query in profile.generated_queries:
                retrieved_articles = search(
                    query_text=process_query(
                        query=query.text, 
                        lang_code=query.query_language,
                        text_processing=preprocessor_config.text_processing),
                    index_dir=lexical_indexer_config.index_dir,
                    max_results=lexical_indexer_config.search.max_results,
                    included_sources=profile.included_sources,
                    covered_period_days=profile.covered_period_days
                ) 
                for article in retrieved_articles:
                    article.profile_id=profile.profile_id
                all_retrieved_articles.extend(retrieved_articles)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
    finally:
        article_repo.save_retrieved_articles(
            retrieved_articles= all_retrieved_articles,
            retrieved_articles_file= newsletter_config.retrieved_articles_file
        )


if __name__ == "__main__":
    main()