"""
Utilities for generating lexical search queries using the configured LLM.
"""

import json

from models.queries import SearchQuery
from llm.client import LLMClient


def generate_queries(
    interest_profile: str,
    source_languages: list[str],
    client: LLMClient,
    prompt: str
) -> list[SearchQuery] | None:
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

    all_generated_queries: list[SearchQuery] = []

    for language in source_languages:

        generated_queries = _generate_queries_for_language(
            interest_summary=interest_profile,
            target_language=language,
            client=client,
            prompt=prompt
        )

        if generated_queries is None:
            continue

        all_generated_queries.extend(generated_queries)

    if not all_generated_queries:
        return None

    return all_generated_queries

def _generate_queries_for_language(
    interest_summary: str,
    target_language: str,
    client: LLMClient,
    prompt: str
) -> list[SearchQuery] | None:
    """
    Generate lexical search queries for a single target language.

    Args:
        interest_profile:
            A profile representing the user's interests.

        target_language:
            Language in which the lexical queries should be generated.

    Returns:
        The generated queries, or None if generation failed.
    """

    prompt = prompt.format(
        INTEREST_PROFILE=interest_summary,
        TARGET_LANGUAGE=target_language,
    )

    queries_txt = client.generate(prompt).strip()

    if queries_txt.startswith("```json"):
        queries_txt = queries_txt[7:]

    if queries_txt.endswith("```"):
        queries_txt = queries_txt[:-3]

    queries_txt = queries_txt.strip()

    try:
        queries_list = json.loads(queries_txt)
    except json.JSONDecodeError:
        return None

    if not isinstance(queries_list, list):
        return None

    final_queries = [
        SearchQuery(
            text=query.strip(),
            query_language= target_language
        )
        for query in queries_list
        if isinstance(query, str) and query.strip()
    ]

    return final_queries