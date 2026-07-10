from dataclasses import dataclass
from pathlib import Path

from typing import TypeVar, Generic

ContentT = TypeVar("ContentT")

@dataclass
class PromptConfig:
    interest_summary: Path
    query_generation: Path


@dataclass
class LLMConfig:
    models: list[str]
    models_retry_delay_seconds: int
    api_base: str
    temperature: float
    max_retries: int
    timeout: float
    prompts: PromptConfig

@dataclass
class LLMResponse(Generic[ContentT]):
    content: ContentT
    model: str