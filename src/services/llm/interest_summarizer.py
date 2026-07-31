"""
Utilities for summarizing user interests using the configured LLM.
"""

from src.llm.client import LLMClient


def summarize_interests(
    interest_description: str,
    selected_keywords: list[str],
    client: LLMClient,
    prompt: str
) -> str | None:
    """
    Generate a concise summary of the user's interests.

    Args:
        interest_description:
            Natural language description of the user's interests.

        selected_keywords:
            List of keywords related to the user's interests.

    Returns:
        The generated summary, or None if no configured model is available.
    """

    prompt = prompt.format(
        INTEREST_DESCRIPTION=interest_description,
        SELECTED_KEYWORDS=", ".join(selected_keywords),
    )

    return client.generate(prompt)