from dataclasses import dataclass
from pathlib import Path
import yaml

from src.crawler.types import CrawlerConfig


@dataclass
class PipelineConfig:
    """Configuration for the whole application."""
    crawler: CrawlerConfig


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
        )
    )