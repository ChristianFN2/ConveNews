"""
Extracts content from articles listed in a JSONL file and saves the
extracted content to another JSONL file.
Also generates per-source statistics in JSONL format.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import trafilatura


def _load_state(state_file: str) -> dict[str, datetime]:
    """
    Load the extraction state.

    Returns:
        Dictionary mapping each processed URL to its extraction timestamp.
    """
    state: dict[str, datetime] = {}

    path = Path(state_file)

    if not path.exists():
        return state

    with path.open("r", encoding="utf-8") as infile:
        for line in infile:
            try:
                record = json.loads(line)

                state[record["url"]] = datetime.fromisoformat(
                    record["extracted_at"]
                )

            except Exception:
                continue

    return state

def _save_state(
    state_file: str,
    state: dict[str, datetime]
) -> None:
    """
    Save the extraction state.
    """

    with open(state_file, "w", encoding="utf-8") as outfile:
        for url, extracted_at in state.items():
            outfile.write(
                json.dumps(
                    {
                        "url": url,
                        "extracted_at": extracted_at.isoformat()
                    },
                    ensure_ascii=False
                )
            )
            outfile.write("\n")

def _cleanup_state_and_articles(
    extracted_articles_file: str,
    state: dict[str, datetime],
    retention_days: int
) -> None:
    """
    Remove obsolete articles from both the extraction state and the extracted
    articles file.

    Articles whose extraction date is older than the configured retention
    period are discarded.
    """

    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

    expired_urls = {
        url
        for url, extracted_at in state.items()
        if extracted_at < cutoff
    }

    if not expired_urls:
        return

    for url in expired_urls:
        del state[url]

    articles_path = Path(extracted_articles_file)
    temp_path = articles_path.with_suffix(".tmp")

    with (
        articles_path.open("r", encoding="utf-8") as infile,
        temp_path.open("w", encoding="utf-8") as outfile,
    ):

        for line in infile:
            try:
                article = json.loads(line)

                if article.get("link") not in expired_urls:
                    outfile.write(line)

            except Exception:
                continue

    temp_path.replace(articles_path)

def _download_new_articles(
    collected_articles_file: str,
    extracted_articles_file: str,
    state: dict[str, datetime],
) -> dict[str, dict[str, int]]:
    """
    Download and extract content for articles that have not been processed yet.

    Newly extracted articles are appended to the extracted articles file and
    added to the extraction state to achieve deduplication.

    Returns:
        Per-source statistics for newly discovered articles only.
    """

    source_stats: dict[str, dict[str, int]] = {}

    extraction_time = datetime.now(timezone.utc)

    with (
        open(collected_articles_file, "r", encoding="utf-8") as infile,
        open(extracted_articles_file, "a", encoding="utf-8") as outfile,
    ):

        for line in infile:
            article = json.loads(line)

            source = article.get("source", "unknown")
            url = article.get("link", "")

            if source not in source_stats:
                source_stats[source] = {
                    "attempted": 0,
                    "downloaded": 0,
                    "http_failures": 0,
                    "extraction_failures": 0,
                    "missing_link": 0,
                }

            if not url:
                source_stats[source]["missing_link"] += 1
                source_stats[source]["attempted"] += 1
                continue

            # Already processed articles are ignored.
            if url in state:
                continue

            source_stats[source]["attempted"] += 1

            try:
                response = requests.get(url, timeout=10)

                if not response.ok:
                    source_stats[source]["http_failures"] += 1
                    continue

                extracted = trafilatura.extract(response.text)

                if not extracted:
                    source_stats[source]["extraction_failures"] += 1
                    continue

                article["content"] = extracted

                outfile.write(json.dumps(article, ensure_ascii=False))
                outfile.write("\n")

                state[url] = extraction_time

                source_stats[source]["downloaded"] += 1

            except Exception:
                source_stats[source]["http_failures"] += 1

    return source_stats

def _write_source_stats(
    source_stats: dict[str, dict[str, int]],
    stats_file: str | Path,
    retention_days: int,
) -> None:
    """
    Append per-source extraction statistics to the statistics history.

    Statistics older than the configured retention period are discarded.
    """

    stats_file = Path(stats_file)
    temp_file = stats_file.with_suffix(".tmp")

    execution_time = datetime.now(timezone.utc)
    cutoff = execution_time - timedelta(days=retention_days)

    with (
        temp_file.open("w", encoding="utf-8") as outfile,
    ):

        # Preserve recent historical statistics
        if stats_file.exists():
            with stats_file.open("r", encoding="utf-8") as infile:

                for line in infile:
                    try:
                        report = json.loads(line)

                        report_date = datetime.fromisoformat(report["date"])

                        if report_date >= cutoff:
                            outfile.write(line)

                    except Exception:
                        continue

        # Append today's statistics
        for source, stats in source_stats.items():

            attempted = stats["attempted"]
            downloaded = stats["downloaded"]

            effectiveness = (
                round(downloaded / attempted * 100, 2)
                if attempted > 0 else 0.0
            )

            report = {
                "date": execution_time.isoformat(),
                "source": source,
                "new_articles": attempted,
                "downloaded_articles": downloaded,
                "effectiveness_percent": effectiveness,
                "http_failures": stats["http_failures"],
                "extraction_failures": stats["extraction_failures"],
                "missing_link": stats["missing_link"],
            }

            outfile.write(json.dumps(report, ensure_ascii=False))
            outfile.write("\n")

    temp_file.replace(stats_file)

def extract_content_from_articles(
    collected_articles_file: str,
    extracted_articles_file: str,
    stats_file: str,
    state_file: str,
    retention_days: int
) -> None:
    """
    Extract article content incrementally.

    Previously extracted articles older than the configured retention period
    are removed before processing new articles.

    Args:
        collected_articles_file:
            JSONL file containing the collected articles.

        extracted_articles_file:
            JSONL file where extracted articles are stored.

        stats_file:
            JSONL file where extraction statistics are written.

        state_file:
            JSONL file used to keep track of previously extracted URLs.

        retention_days:
            Number of days extracted articles are kept before being removed.
    """

    state = _load_state(state_file)

    _cleanup_state_and_articles(
        extracted_articles_file,
        state,
        retention_days
    )

    source_stats = _download_new_articles(
        collected_articles_file,
        extracted_articles_file,
        state
    )

    _save_state(state_file, state)

    _write_source_stats(source_stats, stats_file, retention_days)