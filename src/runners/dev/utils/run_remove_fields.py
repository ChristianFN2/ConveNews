"""
Temporary runner to remove fields from JSONL files.

This script is intended for one-off migrations of the stored data model.
"""

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[4]

FILES = [
    ROOT
    / "data"
    / "output"
    / "temp_collected_articles.jsonl",

    ROOT
    / "data"
    / "output"
    / "extracted_articles.jsonl",
]

FIELDS_TO_REMOVE = [
    "summary",
]


def main() -> None:
    for path in FILES:

        print(f"Processing {path.name}...")

        records = []

        with path.open(
            "r",
            encoding="utf-8",
        ) as infile:

            for line in infile:

                record = json.loads(line)

                for field in FIELDS_TO_REMOVE:
                    record.pop(field, None)

                records.append(record)

        with path.open(
            "w",
            encoding="utf-8",
        ) as outfile:

            for record in records:
                json.dump(
                    record,
                    outfile,
                    ensure_ascii=False,
                )
                outfile.write("\n")

        print(
            f"Done ({len(records)} records)."
        )


if __name__ == "__main__":
    main()