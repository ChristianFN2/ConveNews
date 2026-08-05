from pathlib import Path
import yaml

from src.config.types.application import ApplicationConfig
from src.config.types.crawler import CrawlerConfig
from src.config.types.sources import SourceConfig
from src.config.types.preprocessor import PreprocessorConfig, TextProcessing
from src.config.types.lexical_indexer import LexicalIndexerConfig, SearchConfig
from src.config.types.llm import LLMConfig, PromptConfig
from src.config.types.article_processor import ArticleProcessorConfig
from src.config.types.newsletter import NewsletterConfig


DEFAULT_CONFIG_FILE = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "pipeline.yaml"
)

PROJECT_ROOT = DEFAULT_CONFIG_FILE.parent.parent


def _resolve_path(path: str) -> Path | None:
    """
    Resolve a path relative to the project root.
    """
    if path is None:
        return None
    return (PROJECT_ROOT / path).resolve()


def load_crawler_config() -> CrawlerConfig:
    crawler = _load_config_section("crawler")

    return CrawlerConfig(
            feed_urls_file=_resolve_path(crawler["feed_urls_file"]),
            collected_articles_file=_resolve_path(crawler["collected_articles_file"]),
            extracted_articles_file=_resolve_path(crawler["extracted_articles_file"]),
            max_articles_per_feed=crawler["max_articles_per_feed"],
            collection_window_days=crawler["collection_window_days"],
            extraction_retention_days=crawler["extraction_retention_days"]
        )

def load_preprocessor_config() -> PreprocessorConfig:
    preprocessor = _load_config_section("preprocessor")

    return PreprocessorConfig(
            input_articles_file=_resolve_path(preprocessor["input_articles_file"]),
            processed_articles_file=_resolve_path(preprocessor["processed_articles_file"]),
            text_processing=TextProcessing(**preprocessor["text_processing"])
        )

def load_lexical_indexer_config() -> LexicalIndexerConfig:
    lexical_indexer = _load_config_section("lexical_indexer")

    return LexicalIndexerConfig(
            input_articles_file=_resolve_path(lexical_indexer["input_articles_file"]),
            index_dir=_resolve_path(lexical_indexer["index_dir"]),
            search=SearchConfig(
                max_results=lexical_indexer["search"]["max_results"],
            )
        )

def load_llm_config() -> LLMConfig:
    llm = _load_config_section("llm")

    return LLMConfig(
            models=llm["models"],
            models_retry_delay_seconds=llm["models_retry_delay_seconds"],
            api_base=llm["api_base"],
            temperature=llm["temperature"],
            max_retries=llm["max_retries"],
            timeout=llm["timeout"],
            prompts=PromptConfig(
                interest_summary=_resolve_path(llm["prompts"]["interest_summary"]),
                query_generation=_resolve_path(llm["prompts"]["query_generation"]),
                relevance_evaluation=_resolve_path(llm["prompts"]["relevance_evaluation"])
            ),
        )

def load_article_processor_config() -> ArticleProcessorConfig:
    article_processor = _load_config_section("article_processor")

    return ArticleProcessorConfig(
            selection_margin=article_processor["selection_margin"],
            selected_articles_file=_resolve_path(article_processor["selected_articles_file"])
        )

def load_newsletter_config() -> NewsletterConfig:
    newsletter = _load_config_section("newsletter")

    return NewsletterConfig(
            newsletter_profiles=_resolve_path(
                newsletter["newsletter_profiles"],
            ),
            relevance_threshold=newsletter["relevance_threshold"],
            candidate_articles_file= _resolve_path(newsletter["candidate_articles_file"]),
            evaluated_articles_file= _resolve_path(newsletter["evaluated_articles_file"]),
            newsletters_file= _resolve_path(newsletter["newsletters_file"]),
            average_reading_speed_wpm= newsletter["average_reading_speed_wpm"],
            newsletter_template= _resolve_path(newsletter["templates"]["newsletter_template"]),
            article_template= _resolve_path(newsletter["templates"]["article_template"]),
        )

def load_source_config() -> SourceConfig:
    sources = _load_config_section("sources")

    return SourceConfig(
            sources_file=_resolve_path(sources["sources_file"]),
        )

def load_application_config() -> ApplicationConfig:
    app = _load_config_section("application")

    return ApplicationConfig(
        site_url= app["site_url"],
        about_url= app["about_url"]
    )

def _load_config_section(section: str):
    with DEFAULT_CONFIG_FILE.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return raw[section]