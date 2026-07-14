"""
Development runner for testing article relevance evaluation.
"""

import json
import time
from pathlib import Path

from src.config.config_loader import load_config
from src.llm.relevance_evaluator import evaluate_relevance

DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[3]
    / "config"
    / "pipeline.yaml"
)

INPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "output"
    / "selected_articles.jsonl"
)

ARTICLES_FILE = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "output"
    / "extracted_articles.jsonl"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "output"
    / "evaluated_articles.jsonl"
)


def main() -> None:
    """
    Evaluate the relevance of the selected articles for every user
    profile and generate concise summaries.

    Results are written to a JSONL file and printed to the console.
    """
    config = load_config(DEFAULT_CONFIG_FILE)

    article_lookup = {}

    with open(
        ARTICLES_FILE,
        "r",
        encoding="utf-8",
    ) as infile:

        for line in infile:

            try:
                article = json.loads(line)
            except json.JSONDecodeError:
                continue

            link = article.get("link")

            if not link:
                continue

            article_lookup[link] = article

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

                evaluated_articles = {}

                profile_start = time.perf_counter()

                for language, articles in (
                    record["selected_articles"].items()
                ):

                    print(f"[{language}]")
                    print()

                    evaluated = []

                    for j, article in enumerate(
                        articles,
                        start=1,
                    ):

                        print(
                            f"Article {j}/{len(articles)}"
                        )
                        print(
                            f"Title: {article['title']}"
                        )

                        start = time.perf_counter()

                        article_data = article_lookup.get(article["link"])

                        if article_data is None:
                            print("Article content not found.")
                            continue

                        response = evaluate_relevance(
                            article_title=article_data["title"],
                            article_content=article_data["content"],
                            interest_summary=record[
                                "interest_summary"
                            ],
                            target_language=language,
                            config=config.llm,
                        )

                        elapsed = (
                            time.perf_counter() - start
                        )

                        print(
                            f"Relevance: "
                            f"{response.content.relevance_score:.1f}"
                        )
                        print(
                            f"Completed in "
                            f"{elapsed:.1f} s"
                        )
                        print()

                        evaluated.append(
                            {
                                **article,
                                "relevance_score": (
                                    response.content.relevance_score
                                ),
                                "article_summary": (
                                    response.content.article_summary
                                ),
                                "evaluation_model": (
                                    response.model
                                ),
                            }
                        )

                    evaluated_articles[language] = (
                        evaluated
                    )

                profile_elapsed = (
                    time.perf_counter()
                    - profile_start
                )

                output_record = {
                    "user_id": record["user_id"],
                    "profile_id": record["profile_id"],
                    "interest_description": (
                        record["interest_description"]
                    ),
                    "interest_summary": (
                        record["interest_summary"]
                    ),
                    "selected_keywords": (
                        record["selected_keywords"]
                    ),
                    "queries": record["queries"],
                    "evaluated_articles": (
                        evaluated_articles
                    ),
                }

                outfile.write(
                    json.dumps(
                        output_record,
                        ensure_ascii=False,
                    )
                )
                outfile.write("\n")

                print(
                    f"Profile completed in "
                    f"{profile_elapsed:.1f} s"
                )
                print()

    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")


if __name__ == "__main__":
    main()