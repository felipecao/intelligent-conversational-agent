import os


def expose_error_details() -> bool:
    """When true, API/SSE responses may include internal error strings (dev only)."""
    return os.getenv("EXPOSE_ERROR_DETAILS", "false").lower() in ("1", "true", "yes")
