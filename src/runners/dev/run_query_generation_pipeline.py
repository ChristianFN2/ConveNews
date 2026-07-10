"""
Development runner for testing the query generator,
in conjunction with the interest summarizer.
"""

from pathlib import Path
import time

from src.config.config_loader import load_config
from src.llm.interest_summarizer import summarize_interests
from src.llm.query_generator import generate_queries

DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[3]
    / "config"
    / "pipeline.yaml"
)


def main() -> None:
    """
    Load the configuration and test the complete LLM pipeline.

    First all interest summaries are generated.
    Afterwards, lexical queries are generated from those summaries.
    Finally, all results are printed.
    """
    config = load_config(DEFAULT_CONFIG_FILE)

    test_cases = [
        {
            "description": (
                "I am interested in artificial intelligence, machine learning, "
                "large language models, robotics and autonomous systems. "
                "I also enjoy following scientific discoveries and space exploration."
            ),
            "keywords": [],
            "target_languages": ["en", "es"],
        },
        {
            "description": (
                "Me interesan la economía europea, la política internacional, "
                "la transición energética y las energías renovables."
            ),
            "keywords": [
                "European Union",
                "European Central Bank",
                "Renewable energy",
                "Climate policy",
            ],
            "target_languages": ["es", "en"],
        },
        {
            "description": (
                "I enjoy software engineering, distributed systems, "
                "cybersecurity and cloud computing."
            ),
            "keywords": [
                "Python",
                "Docker",
                "Kubernetes",
                "AWS",
            ],
            "target_languages": ["en", "es"],
        },
        {
            "description": (
                "Me interesa seguir la actualidad del FC Barcelona, "
                "la Fórmula 1 y el tenis profesional."
            ),
            "keywords": [
                "FC Barcelona",
                "Formula 1",
                "Carlos Alcaraz",
                "ATP Tour",
            ],
            "target_languages": ["es", "en"],
        },
        {
            "description": "Me interesan los deportes.",
            "keywords": [
                "Formula 1",
                "NBA",
                "Carlos Alcaraz",
                "Champions League",
            ],
            "target_languages": ["es", "en"],
        },
        {
            "description": "I like technology.",
            "keywords": [],
            "target_languages": ["en", "es"],
        },
    ]

    summaries = []
    queries = []

    try:

        print("Generating interest summaries...\n")

        for i, case in enumerate(test_cases, start=1):

            print(f"[Summary {i}/{len(test_cases)}]")

            start = time.perf_counter()

            summaries.append(
                summarize_interests(
                    interest_description=case["description"],
                    selected_keywords=case["keywords"],
                    config=config.llm,
                )
            )

            elapsed = time.perf_counter() - start

            print(f"Completed in {elapsed:.1f} s\n")

        print("Generating lexical queries...\n")

        for i, (case, summary) in enumerate(
            zip(test_cases, summaries),
            start=1,
        ):

            print(f"[Queries {i}/{len(test_cases)}]")

            start = time.perf_counter()

            queries.append(
                generate_queries(
                    interest_profile=summary.content,
                    target_languages=case["target_languages"],
                    config=config.llm,
                )
            )

            elapsed = time.perf_counter() - start

            print(f"Completed in {elapsed:.1f} s\n")

    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        return

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)

    for i, (case, summary, query_response) in enumerate(
        zip(test_cases, summaries, queries),
        start=1,
    ):

        print("=" * 80)
        print(f"Test case {i}")
        print()

        print("Description:")
        print(case["description"])
        print()

        print("Selected keywords:")
        print(", ".join(case["keywords"]) if case["keywords"] else "(none)")
        print()

        print("Target languages:")
        print(", ".join(case["target_languages"]))
        print()

        print("Summary:")
        print(summary.content)
        print()
        print(f"Model: {summary.model}")
        print()

        print("Generated queries:")

        for language, language_queries in query_response.content.items():

            print(f"  [{language}]")

            for query in language_queries:
                print(f"    - {query}")

            print()

        print(f"Model: {query_response.model}")
        print()


if __name__ == "__main__":
    main()