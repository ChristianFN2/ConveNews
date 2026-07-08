from dataclasses import dataclass
from pathlib import Path


@dataclass
class PromptConfig:
    interest_summary: Path
    query_generation: Path


@dataclass
class LLMConfig:
    models: list[str]
    api_base: str
    temperature: float
    max_retries: int
    timeout: float
    prompts: PromptConfig

@dataclass
class LLMResponse:
    text: str
    model: str