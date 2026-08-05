"""
Utilities for evaluating article relevance and generating summaries
using the configured LLM.
"""

import json

from src.models.articles import CandidateArticle, EvaluatedArticle
from src.llm.client import LLMClient


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
    Evaluate an article for a user profile and generate a translated
    title together with a personalized summary in the target language.

    Args:
        candidate_article:
            Candidate article to evaluate.

        article_content:
            Full article content.

        interest_summary:
            Summary describing the user's interests.

        target_language:
            Language in which the title and summary should be generated.

        generated_summary_words:
            Approximate target length of the generated summary in words.

        client:
            LLM client used to generate the evaluation.

        prompt:
            Prompt template used for the evaluation.

    Returns:
        The evaluated article.

    Raises:
        json.JSONDecodeError:
            If the LLM response does not contain valid JSON.
    """

    prompt = prompt.format(
        ARTICLE_TITLE=candidate_article.title,
        ARTICLE_CONTENT=article_content,
        INTEREST_SUMMARY=interest_summary,
        TARGET_LANGUAGE=target_language,
        SUMMARY_WORDS=generated_summary_words
    )

    response_text = client.generate(prompt).strip()

    if response_text.startswith("```json"):
        response_text = response_text[7:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    start = response_text.find("{")
    end = response_text.rfind("}")

    json_text = response_text[start:end + 1]

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