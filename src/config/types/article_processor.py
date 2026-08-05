from dataclasses import dataclass
from pathlib import Path

@dataclass
class ArticleProcessorConfig:
    """Configuration for the article processor."""
    selection_margin: int
    selected_articles_file: Path