import json
import queue
from collections.abc import Iterator

import requests


def _iter_sse_text_deltas(response: requests.Response) -> Iterator[str]:
    """Parse Server-Sent Events (data: JSON lines) and yield text deltas."""
    buffer = ""
    for chunk in response.iter_content(chunk_size=2048):
        if not chunk:
            continue
        buffer += chunk.decode("utf-8", errors="replace")
        while "\n\n" in buffer:
            raw_event, buffer = buffer.split("\n\n", 1)
            for line in raw_event.splitlines():
                line = line.strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].lstrip()
                try:
                    obj = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") == "delta":
                    yield obj.get("text", "") or ""
                elif obj.get("type") == "done":
                    return
                elif obj.get("type") == "error":
                    raise RuntimeError(obj.get("message", "stream error"))


def sse_worker(q: queue.Queue, api_messages: list[dict], api_base_url: str) -> None:
    try:
        url = f"{api_base_url}/chat/stream"
        with requests.post(
            url,
            json={"messages": api_messages},
            stream=True,
            timeout=120,
        ) as resp:
            if resp.status_code != 200:
                try:
                    err = resp.json()
                    detail = err.get("detail", err)
                except (json.JSONDecodeError, ValueError):
                    detail = resp.text or resp.reason
                q.put(("http_error", detail))
                return
            for text in _iter_sse_text_deltas(resp):
                q.put(("delta", text))
            q.put(("done", None))
    except Exception as e:
        q.put(("fatal", e))
