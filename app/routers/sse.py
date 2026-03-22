import json
import logging
import uuid
from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langgraph.graph.state import CompiledStateGraph

from app.config import expose_error_details
from app.routers.models import ChatMessage, ChatStreamRequest

logger = logging.getLogger(__name__)

_STREAM_ERROR_CODE = "CHAT_STREAM_FAILED"
_USER_FACING_STREAM_ERROR = (
    "We couldn't complete your request. Please try again in a moment."
)


async def sse_token_stream(
    body: ChatStreamRequest,
    graph: CompiledStateGraph,
) -> AsyncIterator[bytes]:
    correlation_id = str(uuid.uuid4())
    try:
        lc_messages = _convert_to_langchain_messages(body.messages)

        async for part in graph.astream(
            {"messages": lc_messages},
            stream_mode="messages",
            version="v2",
        ):
            msg = _messages_stream_part_to_message(part)
            if msg is None:
                continue
            text = _message_to_delta_text(msg)
            if not text:
                continue
            payload = json.dumps({"type": "delta", "text": text}, ensure_ascii=False)
            yield f"data: {payload}\n\n".encode("utf-8")

        done = json.dumps({"type": "done"})
        yield f"data: {done}\n\n".encode("utf-8")

    except Exception as e:
        logger.exception(
            "Chat stream failed [correlation_id=%s]",
            correlation_id,
            extra={"correlation_id": correlation_id},
        )
        if expose_error_details():
            message = str(e)
        else:
            message = _USER_FACING_STREAM_ERROR
        err = json.dumps(
            {
                "type": "error",
                "code": _STREAM_ERROR_CODE,
                "message": message,
                "correlation_id": correlation_id,
            },
            ensure_ascii=False,
        )
        yield f"data: {err}\n\n".encode("utf-8")


def _messages_stream_part_to_message(part: Any) -> BaseMessage | None:
    """Normalize LangGraph `stream_mode='messages'` items (v2 dict or v1 tuple)."""
    if isinstance(part, dict) and part.get("type") == "messages":
        data = part.get("data")
        if (
            isinstance(data, tuple)
            and len(data) >= 1
            and isinstance(data[0], BaseMessage)
        ):
            return data[0]
        return None
    if isinstance(part, tuple) and len(part) == 3:
        _ns, mode, payload = part
        if mode == "messages" and isinstance(payload, tuple) and len(payload) >= 1:
            m = payload[0]
            if isinstance(m, BaseMessage):
                return m
    return None


def _message_to_delta_text(msg: BaseMessage) -> str:
    if isinstance(msg, AIMessageChunk):
        return _convert_chunk_to_str(msg)
    if isinstance(msg, AIMessage):
        c = msg.content
        if isinstance(c, str):
            return c
        if isinstance(c, list):
            parts: list[str] = []
            for block in c:
                if isinstance(block, str):
                    parts.append(block)
                elif isinstance(block, dict) and block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
            return "".join(parts)
    return ""


def _convert_chunk_to_str(chunk: AIMessageChunk) -> str:
    content = chunk.content

    if content is None:
        return ""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)

    return ""


def _convert_to_langchain_messages(messages: list[ChatMessage]) -> list[BaseMessage]:
    lc_messages: list[BaseMessage] = []

    for m in messages:
        if m.role == "user":
            lc_messages.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            lc_messages.append(AIMessage(content=m.content))
        else:
            lc_messages.append(SystemMessage(content=m.content))

    return lc_messages
