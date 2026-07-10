from dataclasses import dataclass
from pathlib import Path

@dataclass
class LexicalIndexerConfig:
    input_articles_file: Path
    index_dir: Path
    search: SearchConfig

@dataclass
class SearchConfig:
    max_results: int

@dataclass
class SearchResult:
    """Represents a lexical search result."""
    title: str
    source: str
    published: str
    link: str
    score: float