"""
Entry point for the lexical indexing process.

This script loads the indexing configuration from the default
configuration file and executes the complete indexing process.
"""

from pathlib import Path

from src.config.config_loader import load_config
from src.lexical_indexer.main_indexer import generate_index

DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "pipeline.yaml"
)


def main() -> None:
    """
    Load the indexing configuration and execute the indexing
    pipeline.
    """
    config = load_config(DEFAULT_CONFIG_FILE)
    generate_index(config.lexical_indexer)


if __name__ == "__main__":
    main()