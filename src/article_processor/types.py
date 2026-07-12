from dataclasses import dataclass

@dataclass
class ArticleProcessorConfig:
    """Configuration for the article processor."""
    max_candidates: int