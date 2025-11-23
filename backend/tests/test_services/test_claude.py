"""
Tests for Claude AI service.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.claude import ClaudeService


@pytest.mark.asyncio
async def test_generate_content_stream():
    """Test streaming content generation"""
    service = ClaudeService()

    # Mock the Anthropic client
    with patch.object(service, 'client') as mock_client:
        # Create mock stream
        mock_stream = AsyncMock()
        mock_stream.__aenter__.return_value = mock_stream
        mock_stream.__aexit__.return_value = None

        async def mock_text_stream():
            for chunk in ["Hello", " ", "World", "!"]:
                yield chunk

        mock_stream.text_stream = mock_text_stream()
        mock_client.messages.stream.return_value = mock_stream

        # Generate content
        result = ""
        async for chunk in service.generate_content_stream("Test prompt"):
            result += chunk

        assert result == "Hello World!"


@pytest.mark.asyncio
async def test_generate_content_with_max_tokens():
    """Test content generation with max tokens parameter"""
    service = ClaudeService()

    with patch.object(service, 'client') as mock_client:
        mock_stream = AsyncMock()
        mock_stream.__aenter__.return_value = mock_stream
        mock_stream.__aexit__.return_value = None

        async def mock_text_stream():
            yield "Test"

        mock_stream.text_stream = mock_text_stream()
        mock_client.messages.stream.return_value = mock_stream

        result = ""
        async for chunk in service.generate_content_stream("Test", max_tokens=1000):
            result += chunk

        # Verify max_tokens was passed
        mock_client.messages.stream.assert_called_once()
        call_kwargs = mock_client.messages.stream.call_args[1]
        assert call_kwargs['max_tokens'] == 1000
