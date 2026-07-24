"""
Shared client for interacting with language models.
"""

import time

from llama_index.llms.openai_like import OpenAILike
from openai import APIConnectionError, APITimeoutError

from config.types.llm import LLMConfig, LLMResponse


class LLMClient:

    def __init__(
        self,
        api_key: str,
        llm_config: LLMConfig,
    ):
        self.api_key = (
            api_key
        )
        self.llm_config = (
            llm_config
        )

    _last_successful_model: str | None = None


    def generate(
        self,
        prompt: str
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

        Returns:
            Model response.
        
        Raises:
            KeyboardInterrupt:
                If the operation is interrupted by the user.
        """

        global _last_successful_model

        models = list(self.llm_config.models)

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
                        api_key=self.api_key,
                        api_base=self.llm_config.api_base,
                        temperature=self.llm_config.temperature,
                        max_retries=self.llm_config.max_retries,
                        timeout=self.llm_config.timeout,
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
                f"Retrying in {self.llm_config.models_retry_delay_seconds} seconds..."
            )

            time.sleep(self.llm_config.models_retry_delay_seconds)