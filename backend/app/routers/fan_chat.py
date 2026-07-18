"""Fan chat endpoints with AI integration and Input Guard.

This module handles the conversation between the fan and the Gemini AI.
It implements the prompt injection guard (Input Guard) before passing
the request to the main chat model.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai import gemini_service

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """A single chat message."""
    role: str  # "user" or "model"
    content: str


class ChatRequest(BaseModel):
    """Incoming chat request payload."""
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    """Outgoing chat response payload."""
    reply: str
    is_safe: bool = True
    blocked_reason: str | None = None


@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Handle fan chat requests.
    
    1. Runs the Input Guard to detect prompt injection or policy violations.
    2. If unsafe, returns a polite refusal immediately.
    3. If safe, (future phase) passes to the main Gemini model with tools.
    """
    # ── 1. Input Guard ─────────────────────────────────────────
    guard_result = await gemini_service.check_input_safety(request.message)
    
    if not guard_result.is_safe:
        logger.warning("chat_rejected_by_guard", reason=guard_result.reason)
        # We don't return the raw reason to the user to avoid leaking system instructions
        return ChatResponse(
            reply="I'm sorry, but I can only answer questions related to the stadium, event operations, or fan assistance. How can I help you with your visit today?",
            is_safe=False,
            blocked_reason=guard_result.reason,
        )

    # ── 2. Main Chat with Tools ────────────────────────────────
    from app.services.ai_tools import stadium_tools
    
    reply_text = await gemini_service.chat_with_tools(
        message=request.message,
        chat_history=request.history,
        tools=stadium_tools
    )
    
    return ChatResponse(
        reply=reply_text,
        is_safe=True
    )

@router.get("/test_tool")
async def test_tool_endpoint():
    """Directly test a tool bypassing Gemini."""
    from app.services.ai_tools import get_zone_status
    try:
        res = await get_zone_status("north_stand")
        return {"status": "success", "data": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}

