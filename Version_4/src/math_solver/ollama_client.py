"""
HTTP client for Ollama API with streaming and retries.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, List, Any, TypedDict

import httpx


class OllamaMessage(TypedDict):
    """Type definition for Ollama message format."""
    role: str
    content: str


class OllamaOptions(TypedDict, total=False):
    """Type definition for Ollama generation options."""
    temperature: float
    num_predict: int

logger = logging.getLogger(__name__)


class OllamaClient:
    """HTTP client for Ollama API with streaming and retries."""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self._is_closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Don't close the client here - keep it alive for reuse
        pass

    async def close(self):
        """Explicitly close the client."""
        if not self._is_closed:
            try:
                await self.client.aclose()
                self._is_closed = True
                logger.info("Ollama client closed successfully")
            except Exception as e:
                logger.warning(f"Error closing Ollama client: {e}")
                self._is_closed = True  # Mark as closed even on error

    async def reconnect(self):
        """Reconnect by creating a new httpx client."""
        logger.info("Reconnecting Ollama client...")
        try:
            if not self._is_closed:
                await self.client.aclose()
        except Exception as e:
            logger.warning(f"Error closing old client during reconnection: {e}")
        self.client = httpx.AsyncClient(timeout=self.timeout)
        self._is_closed = False
        logger.info("Ollama client reconnected")

    async def health_check(self) -> bool:
        """Check if the Ollama service is healthy and accessible."""
        try:
            # Try a simple request to check connectivity
            async with self.client.get(
                f"{self.base_url}/api/tags",
                timeout=5.0
            ) as response:
                return response.status_code == 200
        except Exception as e:
            logger.debug(f"Health check failed: {type(e).__name__}: {e}")
            return False

    async def chat_stream(
        self,
        messages: List[OllamaMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        retries: int = 3,
        retry_delay: float = 1.0
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses from Ollama with retry logic and reconnection.

        Yields chunks of response text as they arrive.
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        last_exception = None
        for attempt in range(retries + 1):
            try:
                # Check if client is closed and reconnect if needed
                if self._is_closed:
                    await self.reconnect()

                async with self.client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=self.timeout
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if "message" in data and "content" in data["message"]:
                                    content = data["message"]["content"]
                                    if content:  # Only yield non-empty content
                                        yield content
                                elif data.get("done", False):
                                    break  # End of stream
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse JSON line: {line}")
                                continue

                return  # Success, exit retry loop

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                # Connection issues - try reconnecting
                last_exception = e
                logger.warning(f"Ollama connection failed (attempt {attempt + 1}/{retries + 1}): {type(e).__name__}: {e}")

                if attempt < retries:
                    try:
                        await self.reconnect()
                        logger.info(f"Reconnected successfully, retrying request...")
                    except Exception as reconn_err:
                        logger.error(f"Reconnection failed: {reconn_err}")

                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"Ollama connection failed after {retries + 1} attempts: {type(e).__name__}: {e}")
                    raise last_exception

            except httpx.HTTPStatusError as e:
                # HTTP errors (4xx, 5xx) - don't reconnect, just retry
                last_exception = e
                logger.warning(f"Ollama HTTP error (attempt {attempt + 1}/{retries + 1}): {e.response.status_code} {e.response.reason_phrase}")

                if attempt < retries:
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"Ollama HTTP error after {retries + 1} attempts: {e.response.status_code} {e.response.reason_phrase}")
                    raise last_exception

            except Exception as e:
                # Other unexpected errors
                last_exception = e
                logger.error(f"Unexpected error in Ollama chat stream (attempt {attempt + 1}/{retries + 1}): {type(e).__name__}: {e}")

                if attempt < retries:
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"Unexpected error after {retries + 1} attempts: {type(e).__name__}: {e}")
                    raise last_exception
