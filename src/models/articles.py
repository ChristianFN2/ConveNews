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
    lexical_score: float
    detected_language: str

@dataclass
class CandidateArticle(RetrievedArticle):
    profile_id: int

@dataclass
class EvaluatedArticle(CandidateArticle):
    relevance_score: float
    article_summary: str
    translated_title: str