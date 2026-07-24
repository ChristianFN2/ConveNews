"""
Utilities for generating lexical search queries using the configured LLM.
"""

import json

from models.queries import SearchQuery
from src.services.llm.client import LLMClient
from config.types.llm import LLMResponse


def _generate_queries_for_language(
    interest_profile: str,
    target_language: str,
    client: LLMClient,
    prompt: str
) -> LLMResponse[list[SearchQuery]] | None:
    """
    Generate lexical search queries for a single target language.

    Args:
        interest_profile:
            A profile representing the user's interests.

        target_language:
            Language in which the lexical queries should be generated.

    Returns:
        The generated queries together with the model used, or None if
        generation failed.
    """

    prompt = prompt.format(
        INTEREST_PROFILE=interest_profile,
        TARGET_LANGUAGE=target_language,
    )

    response = client.generate(prompt)

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
        SearchQuery(
            text=query.strip(),
            query_language= target_language
        )
        for query in queries
        if isinstance(query, str) and query.strip()
    ]

    return LLMResponse(
        content=queries,
        model=response.model,
    )


def generate_queries(
    interest_profile: str,
    source_languages: list[str],
    client: LLMClient,
    prompt: str
) -> LLMResponse[list[SearchQuery]] | None:
    """
    Generate lexical search queries for one or more target languages.

    Args:
        interest_profile:
            A profile representing the user's interests.

        target_languages:
            Languages in which lexical queries should be generated.

    Returns:
        A mapping from language to generated queries together with the
        model used. Returns None if generation failed for every language.
    """
    models_used: list[str] = []

    generated_queries = []

    for language in source_languages:

        response = _generate_queries_for_language(
            interest_profile=interest_profile,
            target_language=language,
            client=client,
            prompt=prompt
        )

        if response is None:
            continue

        generated_queries.extend(response.content)

        if response.model not in models_used:
            models_used.append(response.model)

    if not generated_queries:
        return None

    return LLMResponse(
        content=generated_queries,
        model=", ".join(models_used),
    )