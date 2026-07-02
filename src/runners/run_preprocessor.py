"""
Entry point for the preprocessing process.

This script loads the preprocessing configuration from the default
configuration file and executes the complete preprocessing process.
"""

from pathlib import Path

from src.config.config_loader import load_config
from src.preprocessor.main_preprocessor import apply_preprocessing

DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "config.yaml"
)


def main() -> None:
    """
    Load the preprocessing configuration and execute the preprocessing
    pipeline.
    """
    config = load_config(DEFAULT_CONFIG_FILE)
    apply_preprocessing(config.preprocessor)


if __name__ == "__main__":
    main()