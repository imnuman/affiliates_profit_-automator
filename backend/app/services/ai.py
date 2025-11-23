"""
AI service supporting multiple providers (Anthropic Claude, DeepSeek, OpenAI)
"""
import os
from typing import AsyncGenerator
from openai import AsyncOpenAI
from app.config import settings
from app.core.logging import logger


class AIService:
    """
    Unified AI service that supports multiple providers.

    Supports:
    - Anthropic Claude (via anthropic library)
    - DeepSeek (via OpenAI-compatible API)
    - OpenAI (via openai library)

    Configuration via environment variables:
    - AI_PROVIDER: "anthropic", "deepseek", or "openai" (default: "deepseek")
    - DEEPSEEK_API_KEY: API key for DeepSeek
    - ANTHROPIC_API_KEY: API key for Anthropic
    - OPENAI_API_KEY: API key for OpenAI
    """

    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "deepseek").lower()

        if self.provider == "deepseek":
            # DeepSeek uses OpenAI-compatible API
            api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY or ANTHROPIC_API_KEY must be set")

            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            self.model = "deepseek-chat"
            logger.info("AI Service initialized with DeepSeek provider")

        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY must be set")

            self.client = AsyncOpenAI(api_key=api_key)
            self.model = "gpt-4-turbo-preview"
            logger.info("AI Service initialized with OpenAI provider")

        elif self.provider == "anthropic":
            import anthropic
            api_key = settings.ANTHROPIC_API_KEY
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY must be set")

            self.client = anthropic.AsyncAnthropic(api_key=api_key)
            self.model = "claude-sonnet-4-20250514"
            logger.info("AI Service initialized with Anthropic provider")

        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    async def generate_content_stream(
        self,
        prompt: str,
        max_tokens: int = 2500,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        Generate content with streaming support.

        Args:
            prompt: The prompt for content generation
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)

        Yields:
            Text chunks as they are generated
        """
        if self.provider == "anthropic":
            # Anthropic streaming
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        else:
            # OpenAI-compatible streaming (DeepSeek, OpenAI)
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

    async def generate_content(
        self,
        prompt: str,
        max_tokens: int = 2500,
        temperature: float = 0.7
    ) -> str:
        """
        Generate content without streaming.

        Args:
            prompt: The prompt for content generation
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        if self.provider == "anthropic":
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        else:
            # OpenAI-compatible (DeepSeek, OpenAI)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content

    async def generate_product_review(
        self,
        product_title: str,
        product_description: str,
        tone: str = "professional",
        length: str = "medium"
    ) -> str:
        """Generate a product review."""
        prompt = f"""Write a compelling product review for the following ClickBank product:

Product: {product_title}
Description: {product_description}

Tone: {tone}
Length: {length}

The review should:
- Highlight key features and benefits
- Be honest and balanced
- Include a clear call-to-action
- Be optimized for conversions
- Sound natural and authentic

Write the review now:"""

        return await self.generate_content(prompt)

    async def generate_comparison(
        self,
        products: list,
        tone: str = "professional"
    ) -> str:
        """Generate a product comparison."""
        product_list = "\n".join([
            f"- {p['title']}: {p['description']}" for p in products
        ])

        prompt = f"""Write a detailed comparison of these ClickBank products:

{product_list}

Create a comprehensive comparison that:
- Compares features, pricing, and value
- Highlights pros and cons of each
- Provides a clear recommendation
- Includes a comparison table
- Ends with a strong call-to-action

Tone: {tone}

Write the comparison now:"""

        return await self.generate_content(prompt, max_tokens=3000)


# Create singleton instance
ai_service = AIService()
