"""
Development runner for testing the interest summarizer.
"""

import json
from pathlib import Path

from src.config.config_loader import load_llm_config
from src.services.llm.interest_summarizer import summarize_interests


INPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "input"
    / "newsletter_profiles.jsonl"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "output"
    / "interest_summaries.jsonl"
)


def main() -> None:
    """
    Generate interest summaries for the input user profiles.

    The generated summaries are written to a JSONL file and also printed
    to the console for inspection.
    """
    config = load_llm_config()

    try:

        with (
            open(INPUT_FILE, "r", encoding="utf-8") as infile,
            open(OUTPUT_FILE, "w", encoding="utf-8") as outfile,
        ):

            for i, line in enumerate(infile, start=1):

                try:
                    profile = json.loads(line)
                except json.JSONDecodeError:
                    continue

                print("=" * 80)
                print(f"Profile {i}")
                print()

                print("Interest description:")
                print(profile["interest_description"])
                print()

                print("Selected keywords:")
                if profile["selected_keywords"]:
                    print(", ".join(profile["selected_keywords"]))
                else:
                    print("(none)")
                print()

                response = summarize_interests(
                    interest_description=profile["interest_description"],
                    selected_keywords=profile["selected_keywords"],
                    config=config,
                )

                if response is None:
                    print("Summary:")
                    print("(generation failed)")
                    print()
                    continue

                output_record = {
                    "user_id": profile["user_id"],
                    "profile_id": profile["profile_id"],
                    "target_language": profile["target_language"],
                    "target_article_num": profile["target_article_num"],
                    "included_sources": profile["included_sources"],
                    "covered_time_period_days": profile["covered_time_period_days"],
                    "reading_time_minutes": profile["reading_time_minutes"],
                    "source_languages": profile["source_languages"],
                    "interest_summary": response.content,
                    "model": response.model,
                }

                outfile.write(
                    json.dumps(output_record, ensure_ascii=False)
                )
                outfile.write("\n")

                print("Summary:")
                print(response.content)
                print()

                print(f"Model: {response.model}")
                print()

    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")


if __name__ == "__main__":
    main()