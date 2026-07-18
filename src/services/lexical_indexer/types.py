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
class RetrievedArticle:
    title: str
    source: str
    published: str
    link: str
    score: float

@dataclass
class QueryResult:
    query: str
    results: list[RetrievedArticle]