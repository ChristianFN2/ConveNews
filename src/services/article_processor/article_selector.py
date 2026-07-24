"""
Utilities for selecting the most promising retrieved articles.
"""

from models.articles import RetrievedArticle


def select_candidate_articles(
    candidates: list[RetrievedArticle],
    max_articles: int,
) -> list[RetrievedArticle]:
    """
    Select the best candidate articles

    Args:
        candidates:
            Articles to be potentially chosen

        max_articles:
            Maximum number of articles to return.

    Returns:
        Selected articles ordered by decreasing lexical relevance.
    """

    deduplicated = _deduplicate_articles(candidates)

    deduplicated.sort(
        key=lambda article: article.lexical_score,
        reverse=True,
    )

    return deduplicated[:max_articles]

def _deduplicate_articles(
    articles: list[RetrievedArticle],
) -> list[RetrievedArticle]:
    """
    Remove duplicate articles based on their link.

    If multiple retrieved articles share the same link, only the one
    with the highest lexical score is kept.

    Args:
        articles: Candidate retrieved articles.

    Returns:
        A list containing one article per unique link.
    """
    by_link = {}
    
    for article in articles:
        previous = by_link.get(article.link)

        if (
            previous is None
            or article.lexical_score > previous.lexical_score
        ):
            by_link[article.link] = article

    return list(by_link.values())