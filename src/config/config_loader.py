from dataclasses import dataclass
from pathlib import Path
import yaml

from src.llm.types import LLMConfig, PromptConfig
from src.crawler.types import CrawlerConfig
from src.preprocessor.types import PreprocessorConfig
from src.preprocessor.types import TextProcessing
from src.lexical_indexer.types import LexicalIndexerConfig, SearchConfig
from src.article_processor.types import ArticleProcessorConfig

@dataclass
class PipelineConfig:
    """Configuration for the whole application."""
    crawler: CrawlerConfig
    preprocessor: PreprocessorConfig
    lexical_indexer: LexicalIndexerConfig
    llm: LLMConfig
    article_processor: ArticleProcessorConfig


def _resolve_path(project_root: Path, path: str | None) -> Path | None:
    """
    Resolve a path relative to the project root.
    """
    if path is None:
        return None
    return (project_root / path).resolve()


def load_config(config_file: str | Path) -> PipelineConfig:
    """
    Load application configuration from YAML.

    Paths in the YAML are relative to the project root.
    """
    config_file = Path(config_file).resolve()

    project_root = config_file.parent.parent  # config/ -> project root

    with config_file.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    crawler = raw["crawler"]
    preprocessor = raw["preprocessor"]
    lexical_indexer = raw["lexical_indexer"]
    llm = raw["llm"]
    article_processor = raw["article_processor"]

    return PipelineConfig(
        crawler=CrawlerConfig(
            feed_urls_file=_resolve_path(project_root, crawler["feed_urls_file"]),
            collected_articles_file=_resolve_path(project_root, crawler["collected_articles_file"]),
            extracted_articles_file=_resolve_path(project_root, crawler["extracted_articles_file"]),
            stats_file=_resolve_path(project_root, crawler.get("stats_file")),
            max_articles_per_feed=crawler["max_articles_per_feed"],
            state_file=_resolve_path(project_root, crawler.get("state_file")),
            collection_window_days=crawler["collection_window_days"],
            extraction_retention_days=crawler["extraction_retention_days"]
        ),
        preprocessor=PreprocessorConfig(
            input_articles_file=_resolve_path(project_root, preprocessor["input_articles_file"]),
            processed_articles_file=_resolve_path(project_root, preprocessor["processed_articles_file"]),
            text_processing=TextProcessing(**preprocessor["text_processing"])
        ),
        lexical_indexer=LexicalIndexerConfig(
            input_articles_file=_resolve_path(project_root, lexical_indexer["input_articles_file"]),
            index_dir=_resolve_path(project_root, lexical_indexer["index_dir"]),
            search=SearchConfig(**lexical_indexer["search"])
        ),
        llm=LLMConfig(
            models=llm["models"],
            models_retry_delay_seconds=llm["models_retry_delay_seconds"],
            api_base=llm["api_base"],
            temperature=llm["temperature"],
            max_retries=llm["max_retries"],
            timeout=llm["timeout"],
            prompts=PromptConfig(
                interest_summary=_resolve_path(
                    project_root,
                    llm["prompts"]["interest_summary"],
                ),
                query_generation=_resolve_path(
                    project_root,
                    llm["prompts"]["query_generation"],
                ),
            ),
        ),
        article_processor=ArticleProcessorConfig(
            max_candidates=article_processor["max_candidates"]
        ),
    )