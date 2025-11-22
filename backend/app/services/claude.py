"""
Claude AI service for content generation
"""
import anthropic
from typing import AsyncGenerator
from app.config import settings


class ClaudeService:
    """Claude AI service"""

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_content_stream(
        self,
        prompt: str,
        max_tokens: int = 2500
    ) -> AsyncGenerator[str, None]:
        """
        Generate content with streaming
        """
        async with self.client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def generate_product_review(
        self,
        product_title: str,
        product_description: str,
        tone: str = "professional",
        length: str = "medium"
    ) -> str:
        """
        Generate a product review
        """
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

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    async def generate_comparison(
        self,
        products: list,
        tone: str = "professional"
    ) -> str:
        """
        Generate a product comparison
        """
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

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text


# Create singleton instance
claude_service = ClaudeService()
