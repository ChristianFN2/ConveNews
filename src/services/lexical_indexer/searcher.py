from datetime import datetime, timedelta
from pathlib import Path

from whoosh import index
from whoosh.qparser import MultifieldParser
from whoosh.query import And, DateRange, Or, Term

from src.models.articles import RetrievedArticle


def search(
    query_text: str,
    index_dir: Path,
    max_results: int,
    included_sources: list[str],
    covered_period_days: int,
) -> list[RetrievedArticle]:
    """
    Search the lexical index for the given query.

    Args:
        query_text: Query expressed as keywords.
        index_dir: Directory containing the Whoosh index.
        max_results: Maximum number of results to return.
        included_sources: Source links that should be considered.
        covered_period_days: Maximum age of returned articles.

    Returns:
        A list of search results ordered by decreasing lexical relevance.
    """
    if not index.exists_in(index_dir):
        raise FileNotFoundError(
            f"Whoosh index not found: {index_dir}"
        )

    idx = index.open_dir(index_dir)

    search_fields = [
        "processed_title",
        "processed_content",
    ]

    parser = MultifieldParser(
        search_fields,
        schema=idx.schema,
    )

    lexical_query = parser.parse(query_text)

    earliest_date = (
        datetime.now() -
        timedelta(days=covered_period_days)
    )

    search_filter = And([
        DateRange(
            "published",
            earliest_date,
            None,
        ),
        Or([
            Term("source", source)
            for source in included_sources
        ]),
    ])

    with idx.searcher() as searcher:
        hits = searcher.search(
            lexical_query,
            filter=search_filter,
            limit=max_results,
        )

        return [
            RetrievedArticle(
                title=hit["title"],
                source=hit["source"],
                link=hit["link"],
                published=hit["published"],
                detected_language=hit["detected_language"],
                lexical_score=hit.score,
            )
            for hit in hits
        ]