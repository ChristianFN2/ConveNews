"""
Shared client for interacting with language models.
"""

import os
import time

from llama_index.llms.openai_like import OpenAILike
from openai import APIConnectionError, APITimeoutError

from src.llm.types import LLMConfig, LLMResponse


API_KEY_ENVIRONMENT_VARIABLE = "CONVENEWS_API_KEY"

_last_successful_model: str | None = None


def generate(
    prompt: str,
    config: LLMConfig,
) -> LLMResponse[str]:
    """
    Execute a completion using the first available configured model.

    Models are tried sequentially, prioritising the last one that
    successfully answered. If all configured models are temporarily
    unavailable, the client waits and retries until one responds.
    The operation can be interrupted at any time by raising
    KeyboardInterrupt (for example, by pressing Ctrl+C).

    Args:
        prompt:
            Prompt sent to the language model.

        config:
            LLM configuration.

    Returns:
        Model response.
    
    Raises:
        KeyboardInterrupt:
            If the operation is interrupted by the user.
        RuntimeError:
            If the API key environment variable is not defined.
    """

    api_key = os.getenv(API_KEY_ENVIRONMENT_VARIABLE)

    if api_key is None:
        raise RuntimeError(
            f"Environment variable '{API_KEY_ENVIRONMENT_VARIABLE}' "
            "is not defined."
        )

    global _last_successful_model

    models = list(config.models)

    if (
        _last_successful_model is not None
        and _last_successful_model in models
    ):
        index = models.index(_last_successful_model)

        models = (
            models[index:]
            + models[:index]
        )

    while True:

        for model in models:

            try:
                print(f"Trying model '{model}'...")
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
                print(f"Model '{model}' responded successfully.")
                return LLMResponse(
                    content=response.text,
                    model=model,
                )

            except (APITimeoutError):
                print(
                    f"Model '{model}' unavailable "
                )
                continue
            except APIConnectionError:
                print(
                    f"Connection failed, check if VPN is active"
                )
                continue

        print(
            "All configured models are currently unavailable. "
            f"Retrying in {config.models_retry_delay_seconds} seconds..."
        )

        time.sleep(config.models_retry_delay_seconds)