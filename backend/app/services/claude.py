"""
Claude AI service for content generation

DEPRECATED: Use app.services.ai.AIService instead
This file maintained for backward compatibility
"""
from typing import AsyncGenerator
from app.services.ai import ai_service


class ClaudeService:
    """
    Claude AI service wrapper (delegates to AIService)

    This class is maintained for backward compatibility.
    New code should use app.services.ai.ai_service directly.
    """

    async def generate_content_stream(
        self,
        prompt: str,
        max_tokens: int = 2500
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming (delegates to AIService)"""
        async for chunk in ai_service.generate_content_stream(prompt, max_tokens):
            yield chunk

    async def generate_product_review(
        self,
        product_title: str,
        product_description: str,
        tone: str = "professional",
        length: str = "medium"
    ) -> str:
        """Generate a product review (delegates to AIService)"""
        return await ai_service.generate_product_review(
            product_title, product_description, tone, length
        )

    async def generate_comparison(
        self,
        products: list,
        tone: str = "professional"
    ) -> str:
        """Generate a product comparison (delegates to AIService)"""
        return await ai_service.generate_comparison(products, tone)


# Create singleton instance
claude_service = ClaudeService()
