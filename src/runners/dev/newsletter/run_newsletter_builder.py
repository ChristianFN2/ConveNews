"""
Build HTML newsletters from evaluated articles.
"""

from src.utils.datetime_utils import get_current_day
import json
from pathlib import Path
import time

from src.config.config_loader import load_newsletter_config
from src.services.newsletter.newsletter_builder import (
    build_newsletter,
)
from src.services.newsletter.types import (
    NewsletterContent, NewsletterArticle
)


INPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "output"
    / "evaluated_articles.jsonl"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "output"
    / "newsletters.jsonl"
)

CONVENEWS_URL = (
    "https://github.com/ChristianFN2/ConveNews"
)

ABOUT_URL = (
    "https://github.com/ChristianFN2/ConveNews#readme-ov-file"
)

DEFAULT_PROFILE_TITLE = (
    "My Newsletter"
)


def main() -> None:
    """
    Build one newsletter for every user profile.
    """

    config = load_newsletter_config()

    with (
        open(
            INPUT_FILE,
            "r",
            encoding="utf-8",
        ) as infile,
        open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8",
        ) as outfile,
    ):

        for i, line in enumerate(
            infile,
            start=1,
        ):

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

            start = time.perf_counter()

            all_articles = []

            for articles in record[
                "evaluated_articles"
            ].values():

                all_articles.extend(
                    NewsletterArticle(
                        title=article["title"],
                        source=article["source"],
                        link=article["link"],
                        published=article["published"],
                        article_summary=article[
                            "article_summary"
                        ],
                        relevance_score=article[
                            "relevance_score"
                        ],
                    )
                    for article in articles
                )

            content = NewsletterContent(
                profile_title=record[
                    "profile_title"
                ],
                interest_description=record[
                    "interest_description"
                ],
                keywords=record[
                    "selected_keywords"
                ],
                articles=all_articles,
                generation_date=get_current_day(),
                target_language=record["target_language"],
                convenews_url=CONVENEWS_URL,
                about_url=ABOUT_URL,
            )

            newsletter = build_newsletter(
                content,
                config=config,
            )

            print(
                f"{len(all_articles)} "
                f"candidate articles"
            )

            output_record = {
                "user_id": record["user_id"],
                "profile_id": record["profile_id"],
                "profile_title": record[
                    "profile_title"
                ],
                "interest_description": record[
                    "interest_description"
                ],
                "interest_summary": record[
                    "interest_summary"
                ],
                "selected_keywords": record[
                    "selected_keywords"
                ],
                "newsletter": newsletter.html,
            }

            outfile.write(
                json.dumps(
                    output_record,
                    ensure_ascii=False,
                )
            )

            outfile.write("\n")

            elapsed = (
                time.perf_counter()
                - start
            )

            print(
                f"Completed in "
                f"{elapsed:.1f} s"
            )

            print()


if __name__ == "__main__":
    main()