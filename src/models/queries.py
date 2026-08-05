from dataclasses import dataclass


@dataclass
class SearchQuery:
    text: str
    query_language: str
