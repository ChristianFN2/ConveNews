"""
Development runner for testing the query generator.
"""

from src.config.config_loader import load_llm_config, load_newsletter_config, load_source_config
from src.services.llm.query_generator import generate_queries
from src.repositories.profile_repository import ProfileRepository
from src.repositories.source_repository import SourceRepository
from src.llm.client_provider import create_llm_client


def main() -> None:
    """
    Generate lexical queries from previously generated interest summaries.

    The generated queries are written to a JSONL file
    """
    llm_config = load_llm_config()
    newsletter_config = load_newsletter_config()
    source_config = load_source_config()

    profile_repo = ProfileRepository()
    source_repo = SourceRepository()

    newsletter_profiles = profile_repo.load_newsletter_profiles(
        newsletter_profiles_file= newsletter_config.newsletter_profiles
    )
    client = create_llm_client(llm_config)
    prompt = llm_config.prompts.query_generation.read_text(
        encoding="utf-8"
    )

    try:
        for profile in newsletter_profiles:
            profile_sources = source_repo.load_sources_by_links(
                links=profile.included_sources,
                sources_file= source_config.sources_file
            )
            source_languages = list({
                source.language
                for source in profile_sources
            })
            generated_queries = generate_queries(
                interest_profile=profile.interest_summary,
                source_languages=source_languages,
                client=client,
                prompt=prompt
            )
            profile.generated_queries = generated_queries
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        return
    finally:
        profile_repo.save_newsletter_profiles(
            newsletter_profiles=newsletter_profiles,
            newsletter_profiles_file= newsletter_config.newsletter_profiles
        )


if __name__ == "__main__":
    main()