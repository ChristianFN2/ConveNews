"""
Utilities to build localized HTML newsletters.
"""

import re

from models.articles import EvaluatedArticle
from models.profiles import NewsletterProfile
from models.sources import Source

_MARKER_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def build_newsletter(
    articles: list[EvaluatedArticle],
    profile: NewsletterProfile,
    newsletter_template: str,
    article_template: str,
    sources_by_link: dict[str, Source],
    localization: dict[str, str],
    site_url: str,
    about_url: str,
    generation_date: str
) -> str:
    """
    Build a localized HTML newsletter.

    The builder fills the provided HTML templates by replacing the
    expected template markers with the corresponding newsletter
    content and localized texts.

    Args:
        articles:
            Articles to include in the newsletter.

        profile:
            Newsletter profile used to build the newsletter.

        newsletter_template:
            HTML template of the complete newsletter.

            Expected markers:
                {{LANGUAGE}}
                {{PROFILE_TITLE}}
                {{GENERATED_ON_LABEL}}
                {{GENERATION_DATE}}
                {{PROFILE_DETAILS}}
                {{ARTICLES}}
                {{CONVENEWS_URL}}
                {{CONVENEWS_NAME}}
                {{ABOUT_TEXT}}
                {{ABOUT_URL}}
                {{ABOUT_LINK_LABEL}}

        article_template:
            HTML template of a single newsletter article.

            Expected markers:
                {{ARTICLE_TITLE}}
                {{ARTICLE_SUMMARY}}
                {{SOURCE_LABEL}}
                {{ARTICLE_SOURCE}}
                {{ARTICLE_URL}}
                {{READ_ARTICLE_LABEL}}

        sources_by_link:
            Mapping from source link to the corresponding Source.

        localization:
            Dictionary containing the localized strings required by
            the templates.

        site_url:
            URL of the site.

        about_url:
            URL of the page describing the site.

    Returns:
        The generated newsletter HTML.
    """

    profile_details_html = _build_profile_details_html(
        interest_description= profile.interest_description,
        keywords= profile.selected_keywords,
        localization= localization,
    )

    articles_html = _build_articles_html(
        article_template= article_template,
        articles= articles,
        localization= localization,
        sources_by_link= sources_by_link
    )

    template_values = {
        "LANGUAGE": profile.target_language,
        "PROFILE_TITLE": profile.profile_title,
        "GENERATION_DATE": generation_date,
        "PROFILE_DETAILS": profile_details_html,
        "ARTICLES": articles_html,
        "CONVENEWS_URL": site_url,
        "ABOUT_URL": about_url,
    }

    html = _replace_markers(
        newsletter_template,
        localization,
    )

    html = _replace_markers(
        html,
        template_values,
    )

    return html

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

def _build_articles_html(
    article_template: str,
    articles: list[EvaluatedArticle],
    localization: dict[str, str],
    sources_by_link: dict[str, Source]
) -> str:

    fragments = []

    for article in articles:

        template_values = {
            "ARTICLE_TITLE": article.title,
            "ARTICLE_SUMMARY": article.article_summary,
            "ARTICLE_SOURCE": sources_by_link.get(article.source).name,
            "ARTICLE_URL": article.link,
        }

        html = _replace_markers(
            article_template,
            localization,
        )

        html = _replace_markers(
            html,
            template_values,
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
    marker_to_value: dict[str, str],
) -> str:
    """
    Replace every template marker found in the provided mapping.

    Unknown markers are left unchanged.
    """

    def replace(
        match: re.Match,
    ) -> str:

        marker = match.group(1)

        return marker_to_value.get(
            marker,
            match.group(0),
        )

    return _MARKER_PATTERN.sub(
        replace,
        template,
    )