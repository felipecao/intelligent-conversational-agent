import queue
import threading
import time
from html import escape

import requests
import streamlit as st

from frontend.helpers.chat_history import persist_messages
from frontend.helpers.effects import WAITING_MESSAGES, thinking_html
from frontend.helpers.sse import sse_worker


def transcribe_audio(
    api_base: str, audio_bytes: bytes, filename: str = "audio.wav"
) -> str:
    url = f"{api_base.rstrip('/')}/voice/transcribe"
    r = requests.post(
        url,
        files={"file": (filename, audio_bytes, "audio/wav")},
        timeout=120,
    )
    r.raise_for_status()
    return (r.json().get("text") or "").strip()


TTS_PREP_MESSAGE = "Preparing voice reply…"


def _tts_prep_html(typed: str) -> str:
    safe = escape(typed)
    return (
        f'<p style="margin:0;"><em class="type-caret" '
        f'style="white-space:pre-wrap;">{safe}</em></p>'
    )


def _speak_text_with_typewriter(placeholder, api_base: str, text: str) -> bytes:
    """Run TTS in a thread; animate the prep label with a typewriter loop until done."""
    result: dict[str, object] = {"data": None, "error": None}

    def worker() -> None:
        try:
            result["data"] = speak_text(api_base, text)
        except Exception as e:
            result["error"] = e

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    label = TTS_PREP_MESSAGE
    pos = 0
    while thread.is_alive():
        if pos < len(label):
            pos += 1
            display = label[:pos]
        else:
            placeholder.markdown(_tts_prep_html(label), unsafe_allow_html=True)
            time.sleep(0.25)
            pos = 0
            continue
        placeholder.markdown(_tts_prep_html(display), unsafe_allow_html=True)
        time.sleep(0.04)

    thread.join(timeout=120.0)
    err = result["error"]
    if err is not None:
        raise err
    data = result["data"]
    if not isinstance(data, bytes):
        return b""
    return data


def speak_text(api_base: str, text: str, voice: str = "alloy") -> bytes:
    url = f"{api_base.rstrip('/')}/voice/speak"
    r = requests.post(
        url,
        json={"text": text, "voice": voice},
        timeout=120,
    )
    r.raise_for_status()
    return r.content


def _run_sse_assistant(
    reply_ph,
    api_payload: list[dict],
    api_base_url,
) -> str:
    q: queue.Queue = queue.Queue()
    worker = threading.Thread(
        target=sse_worker, args=(q, api_payload, api_base_url), daemon=True
    )
    worker.start()

    full = ""
    first_delta = False
    msg_idx = 0
    pos = 0

    while True:
        try:
            item = q.get(timeout=0.07)
        except queue.Empty:
            if not first_delta:
                cur = WAITING_MESSAGES[msg_idx % len(WAITING_MESSAGES)]
                if pos < len(cur):
                    pos += 1
                    reply_ph.markdown(thinking_html(cur[:pos]), unsafe_allow_html=True)
                    time.sleep(0.035)
                else:
                    time.sleep(0.4)
                    msg_idx += 1
                    pos = 0
            continue

        kind = item[0]
        if kind == "delta":
            if not first_delta:
                first_delta = True
            full += item[1]
            reply_ph.markdown(full)
        elif kind == "done":
            break
        elif kind == "http_error":
            reply_ph.empty()
            st.error(str(item[1]))
            return ""
        elif kind == "fatal":
            reply_ph.empty()
            st.error(str(item[1]))
            return ""

    return full


def complete_user_turn(user_text: str, *, use_tts: bool, api_base_url: str) -> None:
    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        api_payload = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        reply_ph = st.empty()
        full = _run_sse_assistant(reply_ph, api_payload, api_base_url)

        if full:
            st.session_state.messages.append({"role": "assistant", "content": full})
            persist_messages(st.session_state.messages, api_base_url)
            if use_tts:
                tts_ph = st.empty()
                try:
                    st.session_state["tts_pending"] = _speak_text_with_typewriter(
                        tts_ph, api_base_url, full
                    )
                except Exception:
                    tts_ph.empty()
                    st.caption("Could not synthesize speech for the reply.")
            st.rerun()
