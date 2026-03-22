from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/health")


@router.get("/")
def health_check() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={},
    )
