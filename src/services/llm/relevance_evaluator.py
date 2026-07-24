"""
Utilities for evaluating article relevance and generating summaries
using the configured LLM.
"""

import json

from src.services.llm.client import generate
from config.types.llm import (
    ArticleEvaluation,
    LLMConfig,
    LLMResponse,
)


def evaluate_relevance(
    article_title: str,
    article_content: str,
    interest_summary: str,
    target_language: str,
    config: LLMConfig,
) -> LLMResponse[ArticleEvaluation]:
    """
    Evaluate the relevance of an article for a user profile and
    generate a concise summary.

    Args:
        article_content:
            Full article content.

        interest_summary:
            Interest summary describing the user's interests.

        config:
            LLM configuration.

    Returns:
        The article evaluation together with the model used.
    """
    prompt_template = (
        config.prompts.relevance_evaluation.read_text(
            encoding="utf-8"
        )
    )

    prompt = prompt_template.format(
        ARTICLE_TITLE=article_title,
        ARTICLE_CONTENT=article_content,
        INTEREST_SUMMARY=interest_summary,
        TARGET_LANGUAGE=target_language,
    )

    response = generate(prompt, config)

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

    return LLMResponse(
        content=ArticleEvaluation(
            relevance_score=float(
                evaluation["relevance_score"]
            ),
            article_summary=evaluation[
                "article_summary"
            ].strip(),
        ),
        model=response.model,
    )