"""
Development utility to test the lexical search engine.

This script loads the application configuration, opens the lexical
index and allows interactive keyword searches.
"""

from src.models.sources import Source
from src.config.config_loader import load_lexical_indexer_config, load_source_config
from src.services.lexical_indexer.searcher import search

from src.repositories.source_repository import SourceRepository

def main() -> None:
    """
    Load the search configuration and perform interactive searches.
    """
    indexer_config = load_lexical_indexer_config()
    source_config = load_source_config()

    source_repo = SourceRepository()

    sources: list[Source] = source_repo.load_sources(
        sources_file= source_config.sources_file
    )

    source_links = [
        source.link
        for source in sources
    ]

    print("Lexical search ready (Ctrl+C to exit).")

    while True:
        try:
            query = input("query> ").strip()

            if not query:
                continue

            results = search(
                query_text= query,
                index_dir= indexer_config.index_dir,
                max_results= indexer_config.search.max_results,
                included_sources= source_links,
                covered_period_days= 365
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
                print(f"Score : {result.lexical_score:.4f}")

            print("------------------------------")
            print()

        except KeyboardInterrupt:
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()