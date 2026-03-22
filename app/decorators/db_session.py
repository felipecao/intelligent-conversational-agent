import functools
import inspect
import logging
from collections.abc import Callable
from typing import Any

from sqlmodel import Session

from app.entities.orm_session import engine

logger = logging.getLogger(__name__)

_DB_TOOL_USER_MESSAGE = (
    "A database error occurred while running this action. Please try again."
)


def with_db_session(func: Callable[..., Any]) -> Callable[..., Any]:
    """Inject ``Session(engine)`` as the first argument to ``func``.

    ``func`` must be declared as ``def tool_impl(session: Session, ...)``.

    The returned wrapper hides ``session`` from ``inspect.signature`` so LangChain
    ``@tool`` does not expose it to the model or JSON schema.
    """

    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    if not params or params[0].name != "session":
        raise TypeError(
            f"{func.__qualname__!r} must declare first parameter as 'session: Session'"
        )

    new_sig = sig.replace(parameters=params[1:])

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        with Session(engine) as session:
            try:
                return func(session, *args, **kwargs)
            except Exception:
                logger.exception(
                    "Tool DB operation failed [tool=%s]", func.__qualname__
                )
                return _DB_TOOL_USER_MESSAGE

    wrapper.__signature__ = new_sig  # type: ignore[attr-defined]
    ann = {
        k: v for k, v in getattr(func, "__annotations__", {}).items() if k != "session"
    }
    if "return" in func.__annotations__:
        ann["return"] = func.__annotations__["return"]
    wrapper.__annotations__ = ann
    return wrapper
