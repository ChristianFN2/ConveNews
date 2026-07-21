from pathlib import Path

from whoosh import index
from whoosh.qparser import MultifieldParser

from src.services.lexical_indexer.types import LexicalIndexerConfig
from src.services.lexical_indexer.types import RetrievedArticle


def search(
    query_text: str,
    index_dir: Path,
    max_results: int
) -> list[RetrievedArticle]:
    """
    Search the lexical index for the given query.

    Args:
        query_text: Query expressed as keywords.
        index_config: Lexical index configuration, includes search settings.

    Returns:
        A list of search results ordered by decreasing relevance score.
    """
    if not index.exists_in(index_dir):
        raise FileNotFoundError(
            f"Whoosh index not found: {index_dir}"
        )

    idx = index.open_dir(index_dir)

    SEARCH_FIELDS = [
        "processed_title",
        "processed_content",
    ]

    parser = MultifieldParser(
        SEARCH_FIELDS,
        schema=idx.schema,
    )

    query = parser.parse(query_text)

    with idx.searcher() as searcher:
        hits = searcher.search(query, limit=max_results)

        return [
            RetrievedArticle(
                title=hit["title"],
                source=hit["source"],
                published=hit["published"],
                link=hit["link"],
                score=hit.score,
            )
            for hit in hits
        ]