"""
Development runner for testing the query generator.
"""

from src.config.config_loader import load_llm_config, load_newsletter_config
from src.services.llm.query_generator import generate_queries
from src.repositories.profile_repository import ProfileRepository
from src.repositories.source_repository import SourceRepository
from src.services.llm.client_provider import create_llm_client


def main() -> None:
    """
    Generate lexical queries from previously generated interest summaries.

    The generated queries are written to a JSONL file
    """
    llm_config = load_llm_config()
    newsletter_config = load_newsletter_config()

    profile_repo = ProfileRepository(
        newsletter_profiles_file=newsletter_config.newsletter_profiles
    )
    source_repo = SourceRepository(
        sources_file=""
    )

    newsletter_profiles = profile_repo.load_newsletter_profiles()
    client = create_llm_client(llm_config)
    prompt = llm_config.prompts.query_generation.read_text(
        encoding="utf-8"
    )

    try:
        for profile in newsletter_profiles:
            profile_sources = source_repo.load_sources_by_links(
                profile.included_sources
            )
            source_languages = list({
                source.language
                for source in profile_sources
            })
            response = generate_queries(
                interest_profile=profile.interest_summary,
                source_languages=source_languages,
                client=client,
                prompt=prompt
            )
            profile.generated_queries = response.content
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        return
    finally:
        profile_repo.save_newsletter_profiles(newsletter_profiles=newsletter_profiles)


if __name__ == "__main__":
    main()