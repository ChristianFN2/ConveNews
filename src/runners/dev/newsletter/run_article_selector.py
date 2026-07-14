"""
Development runner for testing article selection.
"""

import json
import time
from pathlib import Path

from src.article_processor.article_selector import (
    select_candidate_articles,
)
from src.config.config_loader import load_config
from src.lexical_indexer.types import (
    QueryResult,
    RetrievedArticle,
)

DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[3]
    / "config"
    / "pipeline.yaml"
)

INPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "output"
    / "retrieved_articles.jsonl"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "output"
    / "selected_articles.jsonl"
)

def main() -> None:
    """
    Select the best candidate articles for every user profile.

    Candidate selection is performed independently for every target
    language and the selected articles are written to a JSONL file.
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
                    print(f"Skipping invalid JSON line {i}.")
                    continue

                print("=" * 80)
                print(f"Profile {i}")
                print()

                print("Interest summary:")
                print(record["interest_summary"])
                print()

                selected_articles = {}

                profile_start = time.perf_counter()

                for language, query_results in (
                    record["retrieval"].items()
                ):

                    print(f"[{language}]")

                    parsed_query_results = []

                    retrieved_count = 0

                    for query_result in query_results:

                        results = [
                            RetrievedArticle(**article)
                            for article in query_result["results"]
                        ]

                        retrieved_count += len(results)

                        parsed_query_results.append(
                            QueryResult(
                                query=query_result["query"],
                                results=results,
                            )
                        )

                    candidate_limit = (
                        config.newsletter.max_articles
                        + config.article_processor.selection_margin
                    )

                    candidates = select_candidate_articles(
                        query_results=parsed_query_results,
                        max_articles=(
                            candidate_limit
                        ),
                    )

                    selected_articles[language] = [
                        article.__dict__
                        for article in candidates
                    ]

                    print(
                        f"Retrieved articles: "
                        f"{retrieved_count}"
                    )
                    print(
                        f"Selected articles : "
                        f"{len(candidates)}"
                    )
                    print()

                elapsed = (
                    time.perf_counter() - profile_start
                )

                output_record = {
                    "user_id": record["user_id"],
                    "profile_id": record["profile_id"],
                    "profile_title": record["profile_title"],
                    "target_language": record["target_language"],
                    "interest_description": (
                        record["interest_description"]
                    ),
                    "selected_keywords": record["selected_keywords"],
                    "interest_summary": record["interest_summary"],
                    "queries": record["queries"],
                    "selected_articles": selected_articles,
                }

                outfile.write(
                    json.dumps(
                        output_record,
                        ensure_ascii=False,
                    )
                )
                outfile.write("\n")

                print(
                    f"Completed in {elapsed:.1f} s"
                )
                print()


    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")


if __name__ == "__main__":
    main()