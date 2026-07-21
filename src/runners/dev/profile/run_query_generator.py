"""
Development runner for testing the query generator.
"""

from src.config.config_loader import load_llm_config, load_newsletter_config
from src.services.llm.query_generator import generate_queries
from src.repositories.profile_repository import ProfileRepository


def main() -> None:
    """
    Generate lexical queries from previously generated interest summaries.

    The generated queries are written to a JSONL file
    """
    llm_config = load_llm_config()
    newsletter_config = load_newsletter_config()

    repo = ProfileRepository(
        newsletter_profiles_file=newsletter_config.newsletter_profiles
    )

    newsletter_profiles = repo.load_newsletter_profiles()

    try:
        for profile in newsletter_profiles:
            response = generate_queries(
                interest_profile=profile.interest_summary,
                source_languages=profile.included_sources,
                config=llm_config
            )
            profile.generated_queries.append(response.content)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        return
    finally:
        repo.save_newsletter_profiles(newsletter_profiles=newsletter_profiles)


if __name__ == "__main__":
    main()