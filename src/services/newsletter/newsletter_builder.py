"""
Utilities to build localized HTML newsletters.
"""

from dataclasses import asdict
from pathlib import Path
import re

from src.services.newsletter.templates.localization import LOCALIZATION
from src.services.newsletter.types import Newsletter, NewsletterContent, NewsletterConfig, NewsletterArticle
from src.services.newsletter.sources import NEWS_SOURCES


_TEMPLATE_DIR = Path(__file__).parent / "templates"

_MARKER_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def build_newsletter(
    content: NewsletterContent,
    config: NewsletterConfig
) -> Newsletter:
    """
    Build a localized HTML newsletter.

    The builder fills the HTML templates by replacing template
    markers with localized texts and newsletter content.
    """

    target_language = content.target_language

    newsletter_template = _load_template(
        "newsletter.html",
    )

    article_template = _load_template(
        "article.html",
    )

    profile_details_html = (
        _build_profile_details_html(
            interest_description=(
                content.interest_description
            ),
            keywords=content.keywords,
            localization=(
                LOCALIZATION[target_language]
            ),
        )
    )

    articles = _select_articles(
        content.articles,
        config,
    )

    articles_html = _build_articles_html(
        article_template=article_template,
        articles=articles,
        localization=LOCALIZATION[target_language],
    )

    values = asdict(content)

    values["PROFILE_DETAILS"] = (
        profile_details_html
    )

    values["ARTICLES"] = articles_html

    values["GENERATION_DATE"] = (
        content.generation_date
    )

    values = {
        key.upper(): str(value)
        for key, value in values.items()
    }

    html = _replace_markers(
        newsletter_template,
        LOCALIZATION[target_language],
    )

    html = _replace_markers(
        html,
        values,
    )

    return Newsletter(html=html)

def _get_source_name(
    source_url: str,
) -> str:
    """
    Return a human-readable source name.
    """

    return NEWS_SOURCES.get(
        source_url,
        source_url,
    )

def _build_profile_details_html(
    interest_description: str,
    keywords: list[str],
    localization: dict[str, str],
) -> str:
    """
    Build the HTML fragment containing profile details.
    """

    if (
        not interest_description
        and not keywords
    ):
        return ""

    parts = []

    if interest_description:
        parts.append(
            f"""
            <p>
                {interest_description}
            </p>
            """
        )

    if keywords:
        keywords_html = _build_keywords_html(
            keywords,
        )

        parts.append(
            keywords_html
        )

    return f"""
    <details>
        <summary>
            {localization["PROFILE_DETAILS_LABEL"]}
        </summary>

        {"".join(parts)}

    </details>
    """

def _select_articles(
    articles: list[NewsletterArticle],
    config: NewsletterConfig,
) -> list[NewsletterArticle]:
    articles = [
        article
        for article in articles
        if (
            article.relevance_score
            >= config.relevance_threshold
        )
    ]

    articles.sort(
        key=lambda article: (
            article.relevance_score
        ),
        reverse=True,
    )

    articles = articles[
        : config.max_articles
    ]

    return articles

def _build_articles_html(
    article_template: str,
    articles: list[NewsletterArticle],
    localization: dict[str, str],
) -> str:

    fragments = []

    for article in articles:

        values = {
            "ARTICLE_TITLE": article.title,
            "ARTICLE_SUMMARY": article.article_summary,
            "ARTICLE_SOURCE": _get_source_name(article.source),
            "ARTICLE_URL": article.link,
        }

        html = _replace_markers(
            article_template,
            localization,
        )

        html = _replace_markers(
            html,
            values,
        )

        fragments.append(html)

    return "\n".join(fragments)


def _build_keywords_html(
    keywords: list[str],
) -> str:

    lines = ["<ul>"]

    for keyword in keywords:
        lines.append(
            f"    <li>{keyword}</li>"
        )

    lines.append("</ul>")

    return "\n".join(lines)


def _replace_markers(
    template: str,
    values: dict[str, str],
) -> str:
    """
    Replace every template marker found in the provided mapping.

    Unknown markers are left unchanged.
    """

    def replace(
        match: re.Match,
    ) -> str:

        marker = match.group(1)

        return values.get(
            marker,
            match.group(0),
        )

    return _MARKER_PATTERN.sub(
        replace,
        template,
    )


def _load_template(
    filename: str,
) -> str:

    path = _TEMPLATE_DIR / filename

    return path.read_text(
        encoding="utf-8",
    )