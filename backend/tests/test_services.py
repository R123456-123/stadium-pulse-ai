import pytest
from app.services.ai import gemini_service
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_chat_with_tools_rate_limit():
    original_client = gemini_service.client
    try:
        mock_chat = AsyncMock()
        mock_chat.send_message.side_effect = Exception("429 ResourceExhausted")
        
        mock_client = MagicMock()
        mock_client.aio.chats.create.return_value = mock_chat
        gemini_service.client = mock_client
        
        response = await gemini_service.chat_with_tools("Hello", [], [])
        assert "stadium network is experiencing extremely high demand" in response
    finally:
        gemini_service.client = original_client

@pytest.mark.asyncio
async def test_chat_with_tools_general_error():
    original_client = gemini_service.client
    try:
        mock_chat = AsyncMock()
        mock_chat.send_message.side_effect = Exception("Unknown Error")
        
        mock_client = MagicMock()
        mock_client.aio.chats.create.return_value = mock_chat
        gemini_service.client = mock_client
        
        response = await gemini_service.chat_with_tools("Hello", [], [])
        assert "trouble connecting to my central systems" in response
    finally:
        gemini_service.client = original_client
