from dataclasses import dataclass
from pathlib import Path


@dataclass
class SourceConfig:
    sources_file: Path