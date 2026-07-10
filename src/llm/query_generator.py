"""
Utilities for generating lexical search queries using the configured LLM.
"""

import json

from src.llm.client import generate
from src.llm.types import LLMConfig, LLMResponse


def _generate_queries_for_language(
    interest_profile: str,
    target_language: str,
    config: LLMConfig,
) -> LLMResponse[list[str]] | None:
    """
    Generate lexical search queries for a single target language.

    Args:
        interest_profile:
            A profile representing the user's interests.

        target_language:
            Language in which the lexical queries should be generated.

        config:
            LLM configuration.

    Returns:
        The generated queries together with the model used, or None if
        generation failed.
    """
    prompt_template = config.prompts.query_generation.read_text(
        encoding="utf-8"
    )

    prompt = prompt_template.format(
        INTEREST_PROFILE=interest_profile,
        TARGET_LANGUAGE=target_language,
    )

    response = generate(prompt, config)

    text = response.content.strip()

    if text.startswith("```json"):
        text = text[7:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    try:
        queries = json.loads(text)
    except json.JSONDecodeError:
        print(
            f"Failed to parse JSON for language '{target_language}':"
        )
        print(text)
        return None

    if not isinstance(queries, list):
        print(
            f"Expected a list of queries for language "
            f"'{target_language}', but got:"
        )
        print(text)
        return None

    queries = [
        query.strip()
        for query in queries
        if isinstance(query, str) and query.strip()
    ]

    return LLMResponse(
        content=queries,
        model=response.model,
    )


def generate_queries(
    interest_profile: str,
    target_languages: list[str],
    config: LLMConfig,
) -> LLMResponse[dict[str, list[str]]] | None:
    """
    Generate lexical search queries for one or more target languages.

    Args:
        interest_profile:
            A profile representing the user's interests.

        target_languages:
            Languages in which lexical queries should be generated.

        config:
            LLM configuration.

    Returns:
        A mapping from language to generated queries together with the
        model used. Returns None if generation failed for every language.
    """
    queries_by_language: dict[str, list[str]] = {}
    models_used: list[str] = []

    for language in target_languages:

        response = _generate_queries_for_language(
            interest_profile=interest_profile,
            target_language=language,
            config=config,
        )

        if response is None:
            continue

        queries_by_language[language] = response.content

        if response.model not in models_used:
            models_used.append(response.model)

    if not queries_by_language:
        return None

    return LLMResponse(
        content=queries_by_language,
        model=", ".join(models_used),
    )