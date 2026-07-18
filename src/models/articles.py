from dataclasses import dataclass


@dataclass
class CollectedArticle:
    title: str
    source: str
    link: str
    published: str

@dataclass
class ExtractedArticle(CollectedArticle):
    content: str

@dataclass
class ProcessedArticle(CollectedArticle):
    processed_title: str
    processed_content: str
    detected_language: str