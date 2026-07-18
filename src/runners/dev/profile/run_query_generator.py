"""
Development runner for testing the query generator.
"""

import json
import time
from pathlib import Path

from src.config.config_loader import load_config
from src.services.llm.query_generator import generate_queries

DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[3]
    / "config"
    / "pipeline.yaml"
)

INPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "output"
    / "interest_summaries.jsonl"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "output"
    / "lexical_queries.jsonl"
)


def main() -> None:
    """
    Generate lexical queries from previously generated interest summaries.

    The generated queries are written to a JSONL file and also printed
    to the console for inspection.
    """
    config = load_config(DEFAULT_CONFIG_FILE)

    try:

        with (
            open(INPUT_FILE, "r", encoding="utf-8") as infile,
            open(OUTPUT_FILE, "w", encoding="utf-8") as outfile,
        ):

            for i, line in enumerate(infile, start=1):

                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                print("=" * 80)
                print(f"Profile {i}")
                print()

                print("Interest description:")
                print(record["interest_description"])
                print()

                print("Interest summary:")
                print(record["interest_summary"])
                print()

                print("Target languages:")
                print(", ".join(record["target_languages"]))
                print()

                start = time.perf_counter()

                response = generate_queries(
                    interest_profile=record["interest_summary"],
                    source_languages=record["source_languages"],
                    config=config.llm,
                )

                elapsed = time.perf_counter() - start

                if response is None:
                    print("Query generation failed.")
                    print()
                    continue

                output_record = {
                    "user_id": record["user_id"],
                    "profile_id": record["profile_id"],
                    "target_language": record["target_language"],
                    "target_article_num": record["target_article_num"],
                    "included_sources": record["included_sources"],
                    "covered_time_period_days": record["covered_time_period_days"],
                    "reading_time_minutes": record["reading_time_minutes"],
                    "queries": response.content,
                    "model": response.model,
                }

                outfile.write(
                    json.dumps(output_record, ensure_ascii=False)
                )
                outfile.write("\n")

                print("Generated queries:")

                for language, language_queries in response.content.items():

                    print(f"  [{language}]")

                    for query in language_queries:
                        print(f"    - {query}")

                    print()

                print(f"Model: {response.model}")
                print(f"Completed in {elapsed:.1f} s")
                print()

    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")


if __name__ == "__main__":
    main()