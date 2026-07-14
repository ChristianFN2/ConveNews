"""
Development runner for testing the interest summarizer.
"""

import json
from pathlib import Path

from src.config.config_loader import load_config
from src.llm.interest_summarizer import summarize_interests

DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[3]
    / "config"
    / "pipeline.yaml"
)

INPUT_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "input"
    / "user_interests.jsonl"
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
    config = load_config(DEFAULT_CONFIG_FILE)

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
                    config=config.llm,
                )

                if response is None:
                    print("Summary:")
                    print("(generation failed)")
                    print()
                    continue

                output_record = {
                    **profile,
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