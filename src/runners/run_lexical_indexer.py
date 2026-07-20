"""
Entry point for the lexical indexing process.

This script loads the indexing configuration 
and executes the complete indexing process.
"""

from src.config.config_loader import load_lexical_indexer_config
from src.services.lexical_indexer.main_indexer import generate_index


def main() -> None:
    """
    Load the indexing configuration and execute the indexing
    pipeline.
    """
    config = load_lexical_indexer_config()
    generate_index(config)


if __name__ == "__main__":
    main()