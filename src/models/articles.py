from dataclasses import dataclass


@dataclass
class Article:
    title: str
    source: str
    link: str
    published: str

@dataclass
class ExtractedArticle(Article):
    content: str

@dataclass
class ProcessedArticle(Article):
    processed_title: str
    processed_content: str
    detected_language: str

@dataclass
class RetrievedArticle(Article):
    profile_id: int
    lexical_score: float
    detected_language: str

@dataclass
class EvaluatedArticle(RetrievedArticle):
    relevance_score: float
    article_summary: str