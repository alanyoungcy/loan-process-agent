"""
GenAI LLM Client
Supports OpenAI and Anthropic with custom base URLs
"""

from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client supporting multiple providers"""

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER

        if self.provider == "openai":
            self.api_key = api_key or settings.OPENAI_API_KEY
            self.base_url = base_url or settings.OPENAI_BASE_URL
            self.model = model or settings.OPENAI_MODEL
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        elif self.provider == "anthropic":
            self.api_key = api_key or settings.ANTHROPIC_API_KEY
            self.base_url = base_url or settings.ANTHROPIC_BASE_URL
            self.model = model or settings.ANTHROPIC_MODEL
            self.client = AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        logger.info(
            f"Initialized LLM client: provider={self.provider}, "
            f"model={self.model}, base_url={self.base_url}"
        )

    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate completion from messages

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with 'content', 'model', 'usage', etc.
        """
        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )

                logger.info(f"OpenAI response type: {type(response)}")
                logger.info(f"OpenAI response: {response}")

                # Handle different response types
                if isinstance(response, str):
                    # API returned a string directly
                    return {
                        "content": response,
                        "model": self.model,
                        "usage": {
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0,
                        },
                        "finish_reason": "stop",
                    }
                elif hasattr(response, 'choices'):
                    # Standard OpenAI response
                    return {
                        "content": response.choices[0].message.content,
                        "model": response.model,
                        "usage": {
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                            "total_tokens": response.usage.total_tokens,
                        },
                        "finish_reason": response.choices[0].finish_reason,
                    }
                else:
                    raise ValueError(f"Unexpected response type: {type(response)}")

            elif self.provider == "anthropic":
                # Convert messages to Anthropic format
                system_message = None
                anthropic_messages = []

                for msg in messages:
                    if msg["role"] == "system":
                        system_message = msg["content"]
                    else:
                        anthropic_messages.append(
                            {"role": msg["role"], "content": msg["content"]}
                        )

                response = await self.client.messages.create(
                    model=self.model,
                    messages=anthropic_messages,
                    system=system_message,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )

                return {
                    "content": response.content[0].text,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.input_tokens
                        + response.usage.output_tokens,
                    },
                    "finish_reason": response.stop_reason,
                }

        except Exception as e:
            logger.error(f"LLM completion error: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            raise

    async def embed(self, text: str) -> List[float]:
        """
        Generate embeddings for text (OpenAI only for now)

        Args:
            text: Text to embed

        Returns:
            List of embedding values
        """
        if self.provider != "openai":
            raise NotImplementedError(
                f"Embeddings not implemented for {self.provider}"
            )

        try:
            response = await self.client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL, input=text
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            raise


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client singleton"""
    global _llm_client

    if _llm_client is None:
        _llm_client = LLMClient()

    return _llm_client


async def generate_completion(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> str:
    """
    Helper function to generate completion from a simple prompt

    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        temperature: Sampling temperature
        max_tokens: Max tokens to generate

    Returns:
        Generated text
    """
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    client = get_llm_client()
    response = await client.complete(
        messages=messages, temperature=temperature, max_tokens=max_tokens
    )

    return response["content"]
