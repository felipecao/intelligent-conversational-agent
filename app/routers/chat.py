from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.agents.customer_support_agent import CustomerSupportAgent
from app.agents.master_data_sub_agent import MasterDataSubAgent
from app.agents.sentiment_analysis_agent import SentimentAnalysisSubAgent
from app.entities.orm_models import Chat
from app.entities.orm_session import SessionDep
from app.repositories.chat_repository import ChatRepository
from app.routers.models import (
    ChatCreateRequest,
    ChatDetailResponse,
    ChatStreamRequest,
    ChatSummaryResponse,
    ChatUpdateRequest,
)
from app.routers.sse import sse_token_stream

router = APIRouter(prefix="/chat")
master_data_subagent = MasterDataSubAgent().build()
sentiment_analysis_subagent = SentimentAnalysisSubAgent().build()
cs_agent = CustomerSupportAgent(
    subagents=[master_data_subagent, sentiment_analysis_subagent]
).build()


@router.get("/", response_model=list[ChatSummaryResponse])
def list_chats(session: SessionDep) -> list[ChatSummaryResponse]:
    repo = ChatRepository(session)
    return [_chat_summary(c) for c in repo.list_all()]


def _chat_summary(chat: Chat) -> ChatSummaryResponse:
    return ChatSummaryResponse(
        id=str(chat.id),
        title=chat.title,
        created_at=chat.created_at.isoformat(),
    )


@router.post(
    "/", response_model=ChatDetailResponse, status_code=status.HTTP_201_CREATED
)
def create_chat(body: ChatCreateRequest, session: SessionDep) -> ChatDetailResponse:
    repo = ChatRepository(session)
    chat = repo.create(body.title, body.chat_history)
    return _chat_detail(chat)


def _chat_detail(chat: Chat) -> ChatDetailResponse:
    return ChatDetailResponse(
        id=str(chat.id),
        title=chat.title,
        created_at=chat.created_at.isoformat(),
        chat_history=list(chat.chat_history or []),
    )


@router.post("/stream")
async def chat_stream(body: ChatStreamRequest) -> StreamingResponse:
    return StreamingResponse(
        sse_token_stream(body, cs_agent),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{chat_id}", response_model=ChatDetailResponse)
def get_chat(chat_id: UUID, session: SessionDep) -> ChatDetailResponse:
    repo = ChatRepository(session)
    chat = repo.get(chat_id)

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )

    return _chat_detail(chat)


@router.patch("/{chat_id}", response_model=ChatDetailResponse)
def update_chat(
    chat_id: UUID, body: ChatUpdateRequest, session: SessionDep
) -> ChatDetailResponse:
    repo = ChatRepository(session)
    chat = repo.update(
        chat_id,
        title=body.title,
        chat_history=body.chat_history,
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )

    return _chat_detail(chat)
