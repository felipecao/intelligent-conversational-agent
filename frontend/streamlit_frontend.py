import hashlib
import os
import sys
from html import escape
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from frontend.helpers.voice import transcribe_audio, complete_user_turn

from frontend.helpers.chat_history import (
    fetch_chat_detail,
    fetch_chat_summaries,
    format_chat_sidebar_label,
    history_to_messages,
)
from frontend.helpers.css_styles import (
    CHAT_BUBBLE_CSS,
    SIDEBAR_CHAT_LIST_CSS,
    THINKING_STYLE,
)

_helpers_dir = Path(__file__).resolve().parent / "helpers"

if str(_helpers_dir) not in sys.path:
    sys.path.insert(0, str(_helpers_dir))

load_dotenv()

API_BASE = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
CHAT_INPUT_KEY = "main_chat_input"


st.set_page_config(
    page_title="Customer Support Chatbot - Intelligent Conversational Agent",
    page_icon="🤖",
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

chats = fetch_chat_summaries(API_BASE)

st.sidebar.header("Previous chats")
st.sidebar.markdown(SIDEBAR_CHAT_LIST_CSS, unsafe_allow_html=True)

if st.sidebar.button(
    "New conversation",
    key="sidebar_new_chat",
    use_container_width=True,
    type="primary" if st.session_state.current_chat_id is None else "secondary",
):
    st.session_state.messages = []
    st.session_state.current_chat_id = None

if not chats:
    st.sidebar.caption("No saved chats yet.")
else:
    st.sidebar.divider()
    for row in chats:
        cid = str(row["id"])
        is_open = st.session_state.current_chat_id == cid
        if st.sidebar.button(
            row["title"],
            key=f"sidebar_chat_{cid}",
            use_container_width=True,
            type="primary" if is_open else "secondary",
        ):
            detail = fetch_chat_detail(cid, API_BASE)
            if detail:
                st.session_state.messages = history_to_messages(
                    detail.get("chat_history", [])
                )
                st.session_state.current_chat_id = cid
            else:
                st.session_state["chat_load_error"] = "Could not load this chat."
        ts = escape(format_chat_sidebar_label(row["created_at"]))
        st.sidebar.markdown(
            f'<p class="sidebar-chat-timestamp">{ts}</p>',
            unsafe_allow_html=True,
        )

if err := st.session_state.pop("chat_load_error", None):
    st.sidebar.error(err)

if err := st.session_state.pop("chat_save_error", None):
    st.sidebar.error(err)

st.title("🤖 Customer Support Chatbot")
st.caption("Here to help you!")

st.markdown(THINKING_STYLE + CHAT_BUBBLE_CSS, unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

audio = st.audio_input("Speak your message", key="voice_input")

if audio is not None:
    audio_bytes = audio.read()
    digest = hashlib.sha256(audio_bytes).hexdigest()

    if digest != st.session_state.get("_voice_digest"):
        try:
            transcript = transcribe_audio(API_BASE, audio_bytes)
        except Exception as e:
            st.error(f"Could not transcribe audio: {e}")
        else:
            if transcript.strip():
                st.session_state[CHAT_INPUT_KEY] = transcript
                st.session_state._tts_after_next = True
                st.session_state._voice_digest = digest
            else:
                st.warning("No speech detected — try again.")

tts_audio = st.session_state.pop("tts_pending", None)

if tts_audio is not None:
    st.caption("Assistant reply (voice)")
    st.audio(tts_audio, format="audio/mpeg")

    components.html(
        """
        <script>
        (function () {
          const w = window.parent;
          try {
            const doc = w.document;
            const el =
              doc.querySelector('[data-testid="stAppViewContainer"]') ||
              doc.querySelector("section.main") ||
              doc.querySelector(".main");
            if (el) {
              el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
              return;
            }
            w.scrollTo({ top: doc.body.scrollHeight, behavior: "smooth" });
          } catch (e) {}
        })();
        </script>
        """,
        height=0,
        width=0,
    )

if prompt := st.chat_input(
    "How can I help you today?",
    key=CHAT_INPUT_KEY,
):
    use_tts = st.session_state.pop("_tts_after_next", False)
    complete_user_turn(prompt, use_tts=use_tts, api_base_url=API_BASE)
