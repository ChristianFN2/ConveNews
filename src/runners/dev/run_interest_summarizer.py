"""
Development runner for testing the interest summarizer.
"""

from pathlib import Path

from src.config.config_loader import load_config
from src.llm.interest_summarizer import summarize_interests

DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[3]
    / "config"
    / "pipeline.yaml"
)


def main() -> None:
    """
    Load the configuration and test the interest summarizer.
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
        },
        {
            "description": (
                "Me interesan los deportes."
            ),
            "keywords": [
                "Formula 1",
                "NBA",
                "Carlos Alcaraz",
                "Champions League",
            ],
        },
        {
            "description": (
                "I like technology."
            ),
            "keywords": [],
        },
    ]

    for i, case in enumerate(test_cases, start=1):
        print("=" * 80)
        print(f"Test case {i}")
        print()

        print("Description:")
        print(case["description"])
        print()

        print("Selected keywords:")
        if case["keywords"]:
            print(", ".join(case["keywords"]))
        else:
            print("(none)")
        print()

        response = summarize_interests(
            interest_description=case["description"],
            selected_keywords=case["keywords"],
            config=config.llm,
        )

        summary= response.text if response is not None else None

        print("Summary:")
        print(summary)
        print("Model:")
        print(response.model if response is not None else None)
        print()


if __name__ == "__main__":
    main()