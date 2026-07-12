"""
Utilities for selecting the most promising retrieved articles.

The selection process is performed independently for each language and
consists of the following steps:

1. Deduplicate retrieved articles across all queries, keeping only the
   occurrence with the highest lexical relevance score.
2. Select the highest-ranked article from every query after
   deduplication.
3. Complete the candidate set with the highest-ranked remaining
   articles until the configured limit is reached.
4. Sort the final candidates by decreasing lexical relevance.

This guarantees article diversity while favouring the most relevant
results returned by the lexical search engine.
"""

from src.lexical_indexer.types import RetrievedArticle, QueryResult


def select_candidate_articles(
    query_results: list[QueryResult],
    max_articles: int,
) -> list[RetrievedArticle]:
    """
    Select the best candidate articles from a set of query results.

    Args:
        query_results:
            Query results for a single language. Each element contains
            the executed query together with its retrieved articles.

        max_articles:
            Maximum number of articles to return.

    Returns:
        Candidate articles ordered by decreasing lexical relevance.
    """
    deduplicated = _deduplicate_articles(query_results)

    candidates = _select_best_per_query(deduplicated)

    candidates = _fill_remaining_candidates(
        deduplicated,
        candidates,
        max_articles,
    )

    return _sort_by_score(candidates)


def _deduplicate_articles(
    query_results: list[QueryResult],
) -> list[QueryResult]:
    """
    Remove duplicate articles across queries.

    If an article appears in multiple queries, it is kept only in the
    query where it achieved the highest lexical score.
    """
    best_occurrence: dict[str, tuple[float, int]] = {}

    for query_index, query in enumerate(query_results):
        for article in query.results:

            current = best_occurrence.get(article.link)

            if (
                current is None
                or article.score > current[0]
            ):
                best_occurrence[article.link] = (
                    article.score,
                    query_index,
                )

    deduplicated = []

    for query_index, query in enumerate(query_results):

        articles = [
            article
            for article in query.results
            if best_occurrence[article.link][1] == query_index
        ]

        articles.sort(
            key=lambda article: article.score,
            reverse=True,
        )

        deduplicated.append(
            QueryResult(
                query=query.query,
                results=articles,
            )
        )

    return deduplicated


def _select_best_per_query(
    query_results: list[QueryResult],
) -> list[RetrievedArticle]:
    """
    Select the highest-ranked article from every query.
    """
    candidates = []

    for query in query_results:

        if query.results:
            candidates.append(query.results[0])

    return candidates


def _fill_remaining_candidates(
    query_results: list[QueryResult],
    candidates: list[RetrievedArticle],
    max_articles: int,
) -> list[RetrievedArticle]:
    """
    Fill the candidate set with the highest-ranked remaining articles.
    """
    if len(candidates) >= max_articles:
        return candidates[:max_articles]

    selected_links = {
        article.link
        for article in candidates
    }

    remaining = []

    for query in query_results:
        for article in query.results:

            if article.link not in selected_links:
                remaining.append(article)

    remaining.sort(
        key=lambda article: article.score,
        reverse=True,
    )

    for article in remaining:

        if len(candidates) >= max_articles:
            break

        candidates.append(article)

    return candidates


def _sort_by_score(
    articles: list[RetrievedArticle],
) -> list[RetrievedArticle]:
    """
    Sort articles by decreasing lexical relevance.
    """
    return sorted(
        articles,
        key=lambda article: article.score,
        reverse=True,
    )