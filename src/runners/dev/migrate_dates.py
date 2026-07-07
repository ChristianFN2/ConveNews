"""
One-time utility to normalize article publication dates to ISO 8601.

This script rewrites the input JSONL file in place.
"""

import json
from pathlib import Path

from src.utils.datetime_utils import parse_datetime, datetime_to_iso


FILES = [
    Path("data/output/collected_articles.jsonl"),
    Path("data/output/extracted_articles.jsonl"),
]


def migrate_file(path: Path) -> None:
    updated = 0
    skipped = 0

    articles = []

    with path.open("r", encoding="utf-8") as infile:
        for line in infile:
            article = json.loads(line)

            published = parse_datetime(article.get("published"))

            if published is None:
                skipped += 1
            else:
                new_value = datetime_to_iso(published)

                if article.get("published") != new_value:
                    article["published"] = new_value
                    updated += 1

            articles.append(article)

    with path.open("w", encoding="utf-8") as outfile:
        for article in articles:
            outfile.write(
                json.dumps(article, ensure_ascii=False) + "\n"
            )

    print(
        f"{path.name}: "
        f"{updated} updated, "
        f"{skipped} skipped"
    )


def main() -> None:
    for file in FILES:
        migrate_file(file)


if __name__ == "__main__":
    main()