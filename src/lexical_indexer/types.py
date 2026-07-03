from dataclasses import dataclass
from pathlib import Path

@dataclass
class LexicalIndexerConfig:
    input_articles_file: Path
    index_dir: Path