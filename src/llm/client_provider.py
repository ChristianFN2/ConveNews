import os

from llm.client import LLMClient
from config.types.llm import LLMConfig


API_KEY_ENVIRONMENT_VARIABLE = "CONVENEWS_API_KEY"

def create_llm_client(config: LLMConfig) -> LLMClient:
    api_key = os.getenv(API_KEY_ENVIRONMENT_VARIABLE)

    if api_key is None:
        raise RuntimeError(
            f"Environment variable '{API_KEY_ENVIRONMENT_VARIABLE}' is not defined."
        )

    return LLMClient(
        api_key=api_key,
        config=config,
    )