import json
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME, STORED
from whoosh.analysis import StemmingAnalyzer
from datetime import datetime

from src.lexical_indexer.types import LexicalIndexerConfig

SCHEMA = Schema(
    url=ID(stored=True, unique=True),
    title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    source=TEXT(stored=True),
    published=DATETIME(stored=True),
    normalized_text=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    original_text=STORED,
    original_summary=STORED,
)

def _parse_published_date(date_string: str) -> datetime | None:
    if not date_string:
        return None
    for fmt in [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
    ]:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    return None


def generate_index(config: LexicalIndexerConfig) -> None:
    if not index.exists_in(config.index_dir):
        idx = index.create_in(config.index_dir, SCHEMA)
    else:
        idx = index.open_dir(config.index_dir)

    writer = idx.writer()
    processed_count = 0
    skipped_count = 0

    with open(config.input_articles_file, "r", encoding="utf-8") as infile:
        for line_num, line in enumerate(infile, start=1):
            try:
                article = json.loads(line)
            except json.JSONDecodeError:
                skipped_count += 1
                continue

            url = article.get("link", "")
            title = article.get("title", "")
            source = article.get("source", "")
            published_text = article.get("published", "")
            published = _parse_published_date(published_text)
            normalized_text = article.get("processed_content", "")
            original_text = article.get("original_content", "")
            original_summary = article.get("original_summary", "")

            if not url:
                skipped_count += 1
                continue

            writer.update_document(
                url=url,
                title=title,
                source=source,
                published=published,
                normalized_text=normalized_text,
                original_text=original_text,
                original_summary=original_summary,
            )
            processed_count += 1

    writer.commit()
    print(f"Indexed {processed_count} documents")
    if skipped_count > 0:
        print(f"Skipped {skipped_count} invalid lines")