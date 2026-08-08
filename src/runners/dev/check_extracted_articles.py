from collections import Counter
from pathlib import Path

from src.utils import jsonl_file_manager as file_manager


ARTICLES_FILE = Path(
    "data/output/extracted_articles.jsonl"
)


def main() -> None:
    records = file_manager.load_jsonl_file(
        ARTICLES_FILE
    )

    source_counts = Counter(
        record["source"]
        for record in records
    )

    links = [
        record["link"]
        for record in records
    ]

    link_counts = Counter(links)

    duplicated_links = {
        link: count
        for link, count in link_counts.items()
        if count > 1
    }

    print(f"Total articles: {len(records)}")
    print(f"Unique links: {len(link_counts)}")
    print(f"Duplicated links: {len(duplicated_links)}")
    print(
        "Duplicate article records: "
        f"{sum(count - 1 for count in duplicated_links.values())}"
    )

    print("\nArticles per source:")

    for source, count in source_counts.most_common():
        print(f"{count:>5}  {source}")

    if duplicated_links:
        print("\nDuplicated links:")

        for link, count in duplicated_links.items():
            print(f"{count}x  {link}")


if __name__ == "__main__":
    main()