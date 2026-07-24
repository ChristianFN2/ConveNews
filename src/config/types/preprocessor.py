from dataclasses import dataclass
from pathlib import Path

@dataclass
class PreprocessorConfig:
    input_articles_file: Path
    processed_articles_file: Path
    text_processing: TextProcessing

@dataclass
class TextProcessing:
    lowercase: bool
    lemmatize: bool
    remove_stopwords: bool
    remove_punctuation: bool
    alphabetic_only: bool