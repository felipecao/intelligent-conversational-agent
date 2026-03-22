from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(
        ..., description="OpenAI-style role"
    )
    content: str = Field(..., min_length=1)


class ChatStreamRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)

    @model_validator(mode="after")
    def last_message_is_user(self) -> Self:
        if self.messages[-1].role != "user":
            raise ValueError("last message must be from the user")
        return self


class ChatSummaryResponse(BaseModel):
    id: str
    title: str
    created_at: str


class ChatDetailResponse(BaseModel):
    id: str
    title: str
    created_at: str
    chat_history: list[dict[str, Any]]


class ChatCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    chat_history: list[dict[str, Any]] = Field(default_factory=list)


class ChatUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    chat_history: list[dict[str, Any]] | None = None


class TranscribeResponse(BaseModel):
    text: str


class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096)
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy"
