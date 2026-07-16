import json
from pathlib import Path

from langdetect import LangDetectException, detect
import spacy

from src.preprocessor.types import PreprocessorConfig, TextProcessing


# Map language codes to spaCy models
LANG_TO_SPACY_MODEL = {
    "es": "es_core_news_sm",
    "en": "en_core_web_sm",
}

# Load spaCy models on demand
_SPACY_MODELS = {}


def _get_spacy_model(lang_code: str):
    """Load and cache spaCy model for a given language."""
    if lang_code not in _SPACY_MODELS:
        model_name = LANG_TO_SPACY_MODEL.get(lang_code)
        if not model_name:
            return None
        try:
            _SPACY_MODELS[lang_code] = spacy.load(model_name)
        except OSError:
            return None
    return _SPACY_MODELS[lang_code]


def _detect_language(text: str) -> str:
    """Detect language code from text."""
    try:
        lang = detect(text)
        return lang.split("-")[0] if lang else "unknown"
    except LangDetectException:
        return "unknown"


def _process_text(
    text: str,
    lang_code: str,
    text_processing: TextProcessing,
) -> str:
    """
    Process text: lowercase, remove stopwords, remove punctuation,
    optionally lemmatize and keep alphabetic tokens only.
    """
    if not text or lang_code == "unknown":
        return ""

    nlp = _get_spacy_model(lang_code)

    if not nlp:
        return ""

    doc = nlp(text)

    tokens = []

    for token in doc:

        if text_processing.remove_stopwords and token.is_stop:
            continue

        if text_processing.remove_punctuation and token.is_punct:
            continue

        if text_processing.alphabetic_only and not token.is_alpha:
            continue

        processed = (
            token.lemma_
            if text_processing.lemmatize
            else token.text
        )

        if text_processing.lowercase:
            processed = processed.lower()

        if not processed.strip():
            continue

        tokens.append(processed)

    return " ".join(tokens)


def _process_article(
    article: dict,
    text_processing: TextProcessing,
) -> dict | None:
    """Preprocess a single article."""
    content = article.get("content", "")

    if not content:
        return None

    lang_code = _detect_language(content)

    processed_content = _process_text(
        content,
        lang_code,
        text_processing,
    )

    processed_title = _process_text(
        article.get("title", ""),
        lang_code,
        text_processing,
    )

    return {
        "title": article.get("title", ""),
        "processed_title": processed_title,
        "source": article.get("source", ""),
        "link": article.get("link", ""),
        "published": article.get("published", ""),
        "detected_language": lang_code,
        "processed_content": processed_content,
    }


def _load_processed_articles(
    processed_articles_file: Path,
) -> dict[str, dict]:
    """
    Load previously processed articles indexed by link.
    """
    processed_articles: dict[str, dict] = {}

    if not processed_articles_file.exists():
        return processed_articles

    with open(
        processed_articles_file,
        "r",
        encoding="utf-8",
    ) as infile:

        for line in infile:
            try:
                article = json.loads(line)
            except json.JSONDecodeError:
                continue

            link = article.get("link")

            if link:
                processed_articles[link] = article

    return processed_articles


def apply_preprocessing(config: PreprocessorConfig) -> None:
    """
    Preprocess the extracted articles dataset.

    Previously processed articles are reused whenever possible.
    Only newly extracted articles are processed again.
    Articles no longer present in the extracted dataset are discarded.
    """
    processed_articles = _load_processed_articles(
        config.processed_articles_file
    )

    with open(
        config.input_articles_file,
        "r",
        encoding="utf-8",
    ) as infile, open(
        config.processed_articles_file,
        "w",
        encoding="utf-8",
    ) as outfile:

        for line in infile:

            try:
                article = json.loads(line)
            except json.JSONDecodeError:
                continue

            link = article.get("link")

            if not link:
                continue

            processed_article = processed_articles.get(link)

            if processed_article is None:
                processed_article = _process_article(
                    article,
                    config.text_processing,
                )

            if processed_article is None:
                continue

            outfile.write(
                json.dumps(
                    processed_article,
                    ensure_ascii=False,
                )
            )
            outfile.write("\n")

def process_query(query: str, lang_code: str, text_processing: TextProcessing) -> str:
    """
    Preprocess a query string
    """

    processed_query = _process_text(
        query,
        lang_code,
        text_processing,
    )

    return processed_query