import logging
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

load_dotenv()

from app.config import expose_error_details  # noqa
from app.routers import chat, health  # noqa

logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(health.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "🤖 Welcome to Customer Support Agent 🤖",
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    correlation_id = str(uuid.uuid4())
    logger.exception(
        "Unhandled exception [correlation_id=%s] path=%s",
        correlation_id,
        request.url.path,
        extra={"correlation_id": correlation_id},
    )

    if expose_error_details():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc), "correlation_id": correlation_id},
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal error occurred. Our team has been notified. Please try again later.",
            "correlation_id": correlation_id,
        },
    )
