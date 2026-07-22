"""
Development runner for the interest summarizer.
"""

from src.config.config_loader import load_llm_config, load_newsletter_config
from src.services.llm.interest_summarizer import summarize_interests
from src.repositories.profile_repository import ProfileRepository
from src.services.llm.client_provider import create_llm_client


def main() -> None:
    """
    Generate interest summaries for the input user profiles.
    """
    llm_config = load_llm_config()
    newsletter_config = load_newsletter_config()

    repo = ProfileRepository(
        newsletter_profiles_file=newsletter_config.newsletter_profiles
    )

    newsletter_profiles = repo.load_newsletter_profiles()

    client = create_llm_client(llm_config)
    prompt = llm_config.prompts.interest_summary.read_text(
        encoding="utf-8"
    )

    try:
        for profile in newsletter_profiles:
            if not profile.is_initialization_pending:
                continue

            response = summarize_interests(
                interest_description=profile.interest_description,
                selected_keywords=profile.selected_keywords,
                client=client,
                prompt=prompt
            )

            profile.interest_summary = response.content
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        return
    finally:
        repo.save_newsletter_profiles(newsletter_profiles=newsletter_profiles)


if __name__ == "__main__":
    main()