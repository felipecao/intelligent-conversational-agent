"""Package import installs a test double for ``with_db_session`` before tool modules load.

A plain identity ``lambda func: func`` would leave ``session`` on the LangChain tool schema,
and Pydantic would reject a ``MagicMock`` as ``sqlmodel.Session``. The real decorator hides
``session`` from the signature; this stub does the same while injecting a ``MagicMock``.
"""

import functools
import inspect
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch


def _test_with_db_session(func: Callable[..., Any]) -> Callable[..., Any]:
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    if not params or params[0].name != "session":
        raise TypeError(
            f"{func.__qualname__!r} must declare first parameter as 'session: Session'"
        )

    new_sig = sig.replace(parameters=params[1:])

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(MagicMock(), *args, **kwargs)

    wrapper.__signature__ = new_sig  # type: ignore[attr-defined]
    ann = {
        k: v for k, v in getattr(func, "__annotations__", {}).items() if k != "session"
    }
    if "return" in func.__annotations__:
        ann["return"] = func.__annotations__["return"]
    wrapper.__annotations__ = ann
    return wrapper


patch("app.decorators.db_session.with_db_session", _test_with_db_session).start()
