"""
Utilities for evaluating article relevance and generating summaries
using the configured LLM.
"""

import json

from models.articles import CandidateArticle, EvaluatedArticle
from src.services.llm.client import LLMClient


def evaluate_relevance(
    candidate_article: CandidateArticle,
    article_content: str,
    interest_summary: str,
    target_language: str,
    generated_summary_words: int,
    client: LLMClient,
    prompt: str
) -> EvaluatedArticle:
    """
    Evaluate the relevance of an article for a user profile and
    generate a concise summary.

    Args:
        article_content:
            Full article content.

        interest_summary:
            Interest summary describing the user's interests.

    Returns:
        The evaluated article
    """

    prompt = prompt.format(
        ARTICLE_TITLE=candidate_article.title,
        ARTICLE_CONTENT=article_content,
        INTEREST_SUMMARY=interest_summary,
        TARGET_LANGUAGE=target_language,
        SUMMARY_WORDS=generated_summary_words
    )

    response = client.generate(prompt)

    text = response.content.strip()

    if text.startswith("```json"):
        text = text[7:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    start = text.find("{")
    end = text.rfind("}")

    json_text = text[start:end + 1]

    evaluation = json.loads(json_text)

    return EvaluatedArticle(
        title= candidate_article.title,
        source= candidate_article.source,
        link= candidate_article.link,
        published= candidate_article.published,
        profile_id= candidate_article.profile_id,
        lexical_score= candidate_article.lexical_score,
        detected_language= candidate_article.detected_language,
        relevance_score= evaluation["relevance_score"],
        article_summary= evaluation["article_summary"],
        translated_title= evaluation["translated_title"],
    )