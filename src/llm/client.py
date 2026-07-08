"""
Shared client for interacting with language models.
"""

import os

from llama_index.llms.openai_like import OpenAILike
from openai import APITimeoutError, APIConnectionError
from src.llm.types import LLMConfig, LLMResponse


class LLMUnavailableError(RuntimeError):
    """
    Raised when none of the configured language models respond.
    """

API_KEY_ENVIRONMENT_VARIABLE = "CONVENEWS_API_KEY"

_last_successful_model: str | None = None


def generate(
    prompt: str,
    config: LLMConfig,
) -> LLMResponse:
    """
    Execute a completion using the first available configured model.

    Models are tried sequentially, prioritising the last one that
    successfully answered.

    Args:
        prompt:
            Prompt sent to the language model.

        config:
            LLM configuration.

    Returns:
        Model response.

    Raises:
        LLMUnavailableError:
            If no configured model responds successfully.
    """

    api_key = os.getenv(API_KEY_ENVIRONMENT_VARIABLE)

    if api_key is None:
        raise RuntimeError(
            f"Environment variable '{API_KEY_ENVIRONMENT_VARIABLE}' is not defined."
        )

    global _last_successful_model

    models = list(config.models)

    if (
        _last_successful_model is not None
        and _last_successful_model in models
    ):
        models.remove(_last_successful_model)
        models.insert(0, _last_successful_model)

    last_exception: Exception | None = None

    for model in models:

        try:

            llm = OpenAILike(
                model=model,
                api_key=api_key,
                api_base=config.api_base,
                temperature=config.temperature,
                max_retries=config.max_retries,
                timeout=config.timeout,
            )

            response = llm.complete(prompt)

            _last_successful_model = model

            return LLMResponse(
                text=response.text,
                model=model,
            )

        except (APITimeoutError, APIConnectionError) as exc:
            last_exception = exc

    raise LLMUnavailableError(
        "No configured language model was available."
    ) from last_exception