from datetime import datetime, timezone

import requests
import streamlit as st


def history_to_messages(history: list) -> list[dict]:
    out: list[dict] = []
    for item in history:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "assistant", "system") and isinstance(content, str):
            out.append({"role": role, "content": content})
    return out


def messages_to_history(messages: list[dict]) -> list[dict]:
    return [{"role": m["role"], "content": m["content"]} for m in messages]


def derive_title(messages: list[dict]) -> str:
    for m in messages:
        if m.get("role") == "user" and isinstance(m.get("content"), str):
            text = m["content"].strip().replace("\n", " ")
            return (text[:80] + "…") if len(text) > 80 else text or "New conversation"
    return "New conversation"


def fetch_chat_summaries(api_base_url: str) -> list[dict]:
    try:
        r = requests.get(f"{api_base_url}/chat/", timeout=30)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []
    except (requests.RequestException, ValueError):
        return []


def fetch_chat_detail(chat_id: str, api_base_url: str) -> dict | None:
    try:
        r = requests.get(f"{api_base_url}/chat/{chat_id}", timeout=30)
        r.raise_for_status()
        return r.json()
    except (requests.RequestException, ValueError):
        return None


def persist_messages(messages: list[dict], api_base_url: str) -> None:
    if not messages:
        return

    payload = {"chat_history": messages_to_history(messages)}
    cid = st.session_state.get("current_chat_id")

    try:
        if cid:
            r = requests.patch(
                f"{api_base_url}/chat/{cid}",
                json=payload,
                timeout=30,
            )
            r.raise_for_status()
        else:
            title = derive_title(messages)
            r = requests.post(
                f"{api_base_url}/chat/",
                json={"title": title, "chat_history": payload["chat_history"]},
                timeout=30,
            )
            r.raise_for_status()
            body = r.json()
            st.session_state.current_chat_id = body.get("id")
    except requests.RequestException:
        st.session_state["chat_save_error"] = "Could not save this chat to the server."


def _parse_created_at(iso: str) -> datetime:
    s = iso.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def format_chat_sidebar_label(created_at: str) -> str:
    dt = _parse_created_at(created_at)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    local = dt.astimezone()
    return local.strftime("%Y-%m-%d %H:%M")
