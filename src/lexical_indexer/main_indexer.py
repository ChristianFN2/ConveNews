import json

from whoosh import index
from whoosh.analysis import RegexTokenizer
from whoosh.fields import DATETIME, ID, TEXT, Schema

from src.lexical_indexer.types import LexicalIndexerConfig
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


def generate_index(config: LexicalIndexerConfig) -> None:
    """
    Build or update the Whoosh lexical index from preprocessed articles.

    The input file must contain one JSON object per line with, at minimum,
    the following fields:

        - processed_title
        - source
        - published
        - link
        - processed_content
        - detected_language

    The processed content is indexed but not stored in the index, while the
    article metadata required to identify each document is stored.
    """
    config.index_dir.mkdir(parents=True, exist_ok=True)

    if not index.exists_in(config.index_dir):
        idx = index.create_in(config.index_dir, SCHEMA)
    else:
        idx = index.open_dir(config.index_dir)

    writer = idx.writer()

    with open(config.input_articles_file, "r", encoding="utf-8") as infile:
        for line in infile:
            try:
                article = json.loads(line)
            except json.JSONDecodeError:
                continue

            link = article.get("link", "")
            if not link:
                continue

            writer.update_document(
                link=link,
                title=article.get("title", ""),
                processed_title=article.get("processed_title", ""),
                source=article.get("source", ""),
                published=parse_datetime(article.get("published", "")),
                detected_language=article.get("detected_language", ""),
                processed_content=article.get("processed_content", ""),
            )

    writer.commit()