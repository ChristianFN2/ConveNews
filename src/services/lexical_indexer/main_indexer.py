from pathlib import Path

from whoosh import index
from whoosh.analysis import RegexTokenizer
from whoosh.fields import DATETIME, ID, TEXT, Schema

from src.models.articles import ProcessedArticle
from src.utils.datetime_utils import parse_datetime


INDEX_ANALYZER = RegexTokenizer()

SCHEMA = Schema(
    link=ID(stored=True, unique=True),
    title=TEXT(stored=True),
    processed_title=TEXT(stored=False, analyzer=INDEX_ANALYZER),
    source=TEXT(stored=True),
    published=DATETIME(stored=True),
    detected_language=ID(stored=True),
    processed_content=TEXT(analyzer=INDEX_ANALYZER, stored=False),
)


def generate_index(
        processed_articles: list[ProcessedArticle],
        index_dir: Path,
    ) -> None:
    """
    Build the Whoosh lexical index from preprocessed articles.
    """
    """
    Create a new lexical index from the given processed articles.
    """
    index_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    ix = index.create_in(
        index_dir,
        SCHEMA,
    )

    writer = ix.writer()

    for article in processed_articles:
        writer.add_document(
            link=article.link,
            title=article.title,
            processed_title=article.processed_title,
            source=article.source,
            published=parse_datetime(article.published),
            detected_language=article.detected_language,
            processed_content=article.processed_content,
        )

    writer.commit()

def update_index(
    processed_articles: list[ProcessedArticle],
    index_dir: Path,
) -> None:
    """
    Synchronize the lexical index with the processed articles.
    """
    if not index.exists_in(index_dir):
        generate_index(
            processed_articles,
            index_dir,
        )
        return

    ix = index.open_dir(index_dir)

    indexed_links = _load_links(index_dir)

    processed_links = {
        article.link
        for article in processed_articles
    }

    articles_to_add = [
        article
        for article in processed_articles
        if article.link not in indexed_links
    ]

    links_to_remove = (
        indexed_links
        - processed_links
    )

    writer = ix.writer()

    for article in articles_to_add:
        writer.add_document(
            link=article.link,
            title=article.title,
            processed_title=article.processed_title,
            source=article.source,
            published=parse_datetime(article.published),
            detected_language=article.detected_language,
            processed_content=article.processed_content,
        )

    for link in links_to_remove:
        writer.delete_by_term(
            "link",
            link,
        )

    writer.commit()


def _load_links(
    ix: index.Index,
) -> set[str]:
    """
    Return the links currently stored in the lexical index.
    """
    
    with ix.searcher() as searcher:
        return {
            fields["link"]
            for fields in searcher.all_stored_fields()
        }