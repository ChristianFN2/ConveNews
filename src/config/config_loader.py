from dataclasses import dataclass
from pathlib import Path
import yaml

from src.services.llm.types import LLMConfig, PromptConfig
from src.services.crawler.types import CrawlerConfig
from src.services.preprocessor.types import PreprocessorConfig
from src.services.preprocessor.types import TextProcessing
from src.services.lexical_indexer.types import LexicalIndexerConfig, SearchConfig
from src.services.article_processor.types import ArticleProcessorConfig
from src.services.newsletter.types import NewsletterConfig
from src.config.types.sources import SourceConfig

DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "pipeline.yaml"
)

PROJECT_ROOT = DEFAULT_CONFIG_FILE.parent.parent


def _resolve_path(project_root: Path, path: str | None) -> Path | None:
    """
    Resolve a path relative to the project root.
    """
    if path is None:
        return None
    return (project_root / path).resolve()


def load_crawler_config() -> CrawlerConfig:
    with DEFAULT_CONFIG_FILE.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    crawler = raw["crawler"]

    return CrawlerConfig(
            feed_urls_file=_resolve_path(PROJECT_ROOT, crawler["feed_urls_file"]),
            collected_articles_file=_resolve_path(PROJECT_ROOT, crawler["collected_articles_file"]),
            extracted_articles_file=_resolve_path(PROJECT_ROOT, crawler["extracted_articles_file"]),
            stats_file=_resolve_path(PROJECT_ROOT, crawler.get("stats_file")),
            max_articles_per_feed=crawler["max_articles_per_feed"],
            state_file=_resolve_path(PROJECT_ROOT, crawler.get("state_file")),
            collection_window_days=crawler["collection_window_days"],
            extraction_retention_days=crawler["extraction_retention_days"]
        )

def load_preprocessor_config() -> PreprocessorConfig:
    with DEFAULT_CONFIG_FILE.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    preprocessor = raw["preprocessor"]

    return PreprocessorConfig(
            input_articles_file=_resolve_path(PROJECT_ROOT, preprocessor["input_articles_file"]),
            processed_articles_file=_resolve_path(PROJECT_ROOT, preprocessor["processed_articles_file"]),
            text_processing=TextProcessing(**preprocessor["text_processing"])
        )

def load_lexical_indexer_config() -> LexicalIndexerConfig:
    with DEFAULT_CONFIG_FILE.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    lexical_indexer = raw["lexical_indexer"]

    return LexicalIndexerConfig(
            input_articles_file=_resolve_path(PROJECT_ROOT, lexical_indexer["input_articles_file"]),
            index_dir=_resolve_path(PROJECT_ROOT, lexical_indexer["index_dir"]),
            search=SearchConfig(**lexical_indexer["search"])
        )

def load_llm_config() -> LLMConfig:
    with DEFAULT_CONFIG_FILE.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    llm = raw["llm"]

    return LLMConfig(
            models=llm["models"],
            models_retry_delay_seconds=llm["models_retry_delay_seconds"],
            api_base=llm["api_base"],
            temperature=llm["temperature"],
            max_retries=llm["max_retries"],
            timeout=llm["timeout"],
            prompts=PromptConfig(
                interest_summary=_resolve_path(
                    PROJECT_ROOT,
                    llm["prompts"]["interest_summary"],
                ),
                query_generation=_resolve_path(
                    PROJECT_ROOT,
                    llm["prompts"]["query_generation"],
                ),
                relevance_evaluation=_resolve_path(
                    PROJECT_ROOT,
                    llm["prompts"]["relevance_evaluation"],
                )
            ),
        )

def load_article_processor_config() -> ArticleProcessorConfig:
    with DEFAULT_CONFIG_FILE.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    article_processor = raw["article_processor"]

    return ArticleProcessorConfig(
            selection_margin=article_processor["selection_margin"]
        )

def load_newsletter_config() -> NewsletterConfig:
    with DEFAULT_CONFIG_FILE.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    newsletter = raw["newsletter"]

    return NewsletterConfig(
            newsletter_profiles=_resolve_path(
                PROJECT_ROOT,
                newsletter["newsletter_profiles"],
            ),
            relevance_threshold=newsletter["relevance_threshold"]
        )

def load_source_config() -> SourceConfig:
    with DEFAULT_CONFIG_FILE.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    sources = raw["sources"]

    return SourceConfig(
            sources_file=_resolve_path(
                PROJECT_ROOT,
                sources["sources_file"],
            ),
        )