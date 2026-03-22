import logging
import os
from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from openai import OpenAI

from app.routers.models import TranscribeResponse, SpeakRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...)) -> TranscribeResponse:
    raw = await file.read()

    if not raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="empty audio upload",
        )

    bio = BytesIO(raw)
    bio.name = file.filename or "audio.wav"
    open_ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        tr = open_ai_client.audio.transcriptions.create(
            model="whisper-1",
            file=bio,
        )
    except Exception:
        logger.exception("Whisper transcription failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Speech transcription failed",
        ) from None

    return TranscribeResponse(text=(tr.text or "").strip())


@router.post("/speak")
def speak(body: SpeakRequest) -> Response:
    try:
        open_ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = open_ai_client.audio.speech.create(
            model="tts-1",
            voice=body.voice,
            input=body.text,
        )
    except Exception:
        logger.exception("TTS failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Text-to-speech failed",
        ) from None

    content = getattr(resp, "content", None)
    if content is None:
        buf = BytesIO()
        resp.stream_to_file(buf)
        content = buf.getvalue()

    return Response(content=content, media_type="audio/mpeg")
