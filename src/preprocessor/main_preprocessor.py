import json

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
            # Model not installed
            return None
    return _SPACY_MODELS[lang_code]


def _detect_language(text: str) -> str:
    """Detect language code from text. Returns 'unknown' if detection fails."""
    try:
        lang = detect(text)
        return lang.split("-")[0] if lang else "unknown"
    except LangDetectException:
        return "unknown"


def _process_text(text: str, lang_code: str, text_processing: TextProcessing) -> str:
    """
    Process text: lowercase, remove stopwords, lemmatize.
    Returns processed text as space-separated lemmas.
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

        if text_processing.lemmatize:
            processed = token.lemma_
        else:
            processed = token.text

        if text_processing.lowercase:
            processed = processed.lower()

        if not processed.strip():
            continue

        tokens.append(processed)

    return " ".join(tokens)

def _process_article(article: dict, text_processing: TextProcessing) -> dict | None:
    """Preprocess a single article."""
    content = article.get("content", "")

    if not content:
        return None

    lang_code = _detect_language(content)
    processed_content = _process_text(content, lang_code, text_processing)

    return {
        "title": article.get("title", ""),
        "source": article.get("source", ""),
        "link": article.get("link", ""),
        "detected_language": lang_code,
        "processed_content": processed_content,
    }


def apply_preprocessing(config: PreprocessorConfig) -> None:
    """
    Preprocess the extracted articles dataset.

    Reads the input JSONL file specified in the configuration, preprocesses
    each article independently and writes the resulting articles to the output
    JSONL file.

    Each line of the input file must contain a JSON object with, at minimum,
    the following fields:

        - title
        - summary
        - content
        - source
        - link
        - published

    Articles without content are skipped. Invalid JSON lines are ignored.
    """
    with open(config.input_articles_file, "r", encoding="utf-8") as infile, \
         open(config.processed_articles_file, "w", encoding="utf-8") as outfile:

        for line in infile:
            try:
                article = json.loads(line)
            except json.JSONDecodeError:
                continue

            processed_article = _process_article(article, config.text_processing)

            if processed_article is None:
                continue

            outfile.write(json.dumps(processed_article, ensure_ascii=False))
            outfile.write("\n")