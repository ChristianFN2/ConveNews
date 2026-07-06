"""
Development utility to test the lexical search engine.

This script loads the application configuration, opens the lexical
index and allows interactive keyword searches.
"""

from pathlib import Path

from src.config.config_loader import load_config
from src.lexical_indexer.searcher import search

DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[3]
    / "config"
    / "pipeline.yaml"
)


def main() -> None:
    """
    Load the search configuration and perform interactive searches.
    """
    config = load_config(DEFAULT_CONFIG_FILE)

    print("Lexical search ready (Ctrl+C to exit).")

    while True:
        try:
            query = input("query> ").strip()

            if not query:
                continue

            results = search(
                query,
                config.lexical_indexer,
            )

            if not results:
                print("No results found.")
                continue

            print()

            for result in results:
                print("------------------------------")
                print(f"Title : {result.title}")
                print(f"Source: {result.source}")
                print(f"Link  : {result.link}")
                print(f"Score : {result.score:.4f}")

            print("------------------------------")
            print()

        except KeyboardInterrupt:
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()