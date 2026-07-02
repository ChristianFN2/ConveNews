"""
Entry point for the crawling pipeline.

This script loads the crawler configuration from the default configuration
file and executes the complete crawling pipeline.
"""

from pathlib import Path

from src.config.config_loader import load_config
from src.crawler.main_crawler import crawl

DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "config.yaml"
)


def main() -> None:
    """
    Load the crawler configuration and execute the crawling pipeline.
    """
    config = load_config(DEFAULT_CONFIG_FILE)
    crawl(config.crawler)


if __name__ == "__main__":
    main()