from dataclasses import dataclass
from pathlib import Path


@dataclass
class PromptConfig:
    interest_summary: Path
    query_generation: Path


@dataclass
class LLMConfig:
    model: str
    api_base: str
    temperature: float
    prompts: PromptConfig