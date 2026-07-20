"""
Entry point for the preprocessing process.

This script loads the preprocessing configuratio 
and executes the complete preprocessing process.
"""

from src.config.config_loader import load_preprocessor_config
from src.services.preprocessor.main_preprocessor import apply_preprocessing


def main() -> None:
    """
    Load the preprocessing configuration and execute the preprocessing
    pipeline.
    """
    config = load_preprocessor_config()
    apply_preprocessing(config)


if __name__ == "__main__":
    main()