"""
Development runner for testing lexical query retrieval.
"""

import json
import time
from pathlib import Path

from src.config.config_loader import load_lexical_indexer_config, load_preprocessor_config
from src.services.lexical_indexer.searcher import search
from src.utils.datetime_utils import datetime_to_iso
from src.services.preprocessor.main_preprocessor import process_query


INPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "output"
    / "lexical_queries.jsonl"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "output"
    / "retrieved_articles.jsonl"
)


def main() -> None:
    """
    Execute all generated lexical queries against the lexical index.

    Retrieved articles are written to a JSONL file and also printed
    to the console for inspection.
    """
    lexical_indexer_config = load_lexical_indexer_config()
    preprocessor_config = load_preprocessor_config()

    try:

        with (
            open(INPUT_FILE, "r", encoding="utf-8") as infile,
            open(OUTPUT_FILE, "w", encoding="utf-8") as outfile,
        ):

            for i, line in enumerate(infile, start=1):

                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    print(
                        f"Skipping invalid JSON line {i}."
                    )
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

                retrieval = {}

                profile_start = time.perf_counter()

                for language, queries in record["queries"].items():

                    print(f"[{language}]")

                    language_results = []

                    for query in queries:

                        print(f"  Query: {query}")

                        start = time.perf_counter()

                        results = search(
                            query_text=process_query(query,language,preprocessor_config.text_processing),
                            index_dir=lexical_indexer_config.index_dir,
                            max_results=lexical_indexer_config.search.max_results
                        ) 

                        elapsed = time.perf_counter() - start

                        print(
                            f"    {len(results)} articles "
                            f"({elapsed:.2f} s)"
                        )

                        language_results.append(
                            {
                                "query": query,
                                "results": [
                                    {
                                        "title": article.title,
                                        "source": article.source,
                                        "link": article.link,
                                        "published": datetime_to_iso(article.published),
                                        "score": article.score,
                                    }
                                    for article in results
                                ],
                            }
                        )

                    retrieval[language] = language_results

                    print()

                profile_elapsed = (
                    time.perf_counter() - profile_start
                )

                output_record = {
                    **record,
                    "retrieval": retrieval,
                }

                outfile.write(
                    json.dumps(
                        output_record,
                        ensure_ascii=False,
                    )
                )
                outfile.write("\n")

                print(
                    f"Completed in {profile_elapsed:.1f} s"
                )
                print()

    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")


if __name__ == "__main__":
    main()