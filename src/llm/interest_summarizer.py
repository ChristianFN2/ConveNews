"""
Utilities for summarizing user interests using the configured LLM.
"""

from src.llm.client import generate
from src.llm.types import LLMConfig, LLMResponse


def summarize_interests(
    interest_description: str,
    selected_keywords: list[str],
    config: LLMConfig,
) -> LLMResponse[str] | None:
    """
    Generate a concise summary of the user's interests.

    Args:
        interest_description:
            Natural language description of the user's interests.

        selected_keywords:
            List of keywords related to the user's interests.

        config:
            LLM configuration.

    Returns:
        The generated summary, or None if no configured model is available.
    """
    prompt_template = config.prompts.interest_summary.read_text(
        encoding="utf-8"
    )

    prompt = prompt_template.format(
        INTEREST_DESCRIPTION=interest_description,
        SELECTED_KEYWORDS=", ".join(selected_keywords),
    )

    return generate(prompt, config)