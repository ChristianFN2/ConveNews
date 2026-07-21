"""
Development runner for the interest summarizer.
"""

from src.config.config_loader import load_llm_config, load_newsletter_config
from src.services.llm.interest_summarizer import summarize_interests
from src.repositories.profile_repository import ProfileRepository


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

    try:
        for profile in newsletter_profiles:
            response = summarize_interests(
                interest_description=profile.interest_description,
                selected_keywords=profile.selected_keywords,
                config=llm_config
            )

            profile.interest_summary = response.content
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")

    repo.save_newsletter_profiles(newsletter_profiles=newsletter_profiles)


if __name__ == "__main__":
    main()