import os
import queue
import sys
import threading
import time
from html import escape
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from frontend.helpers.chat_history import (
    history_to_messages,
    format_chat_sidebar_label,
    fetch_chat_summaries,
    fetch_chat_detail,
    persist_messages,
)
from frontend.helpers.css_styles import (
    THINKING_STYLE,
    CHAT_BUBBLE_CSS,
    SIDEBAR_CHAT_LIST_CSS,
)
from frontend.helpers.effects import WAITING_MESSAGES, thinking_html
from frontend.helpers.sse import sse_worker

_helpers_dir = Path(__file__).resolve().parent / "helpers"
if str(_helpers_dir) not in sys.path:
    sys.path.insert(0, str(_helpers_dir))

load_dotenv()

API_BASE = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
CHAT_LIST_URL = f"{API_BASE}/chat/"


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

if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        api_payload = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        reply_ph = st.empty()

        q: queue.Queue = queue.Queue()
        worker = threading.Thread(
            target=sse_worker, args=(q, api_payload, API_BASE), daemon=True
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
                        reply_ph.markdown(
                            thinking_html(cur[:pos]), unsafe_allow_html=True
                        )
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
                full = ""
                break
            elif kind == "fatal":
                reply_ph.empty()
                st.error(str(item[1]))
                full = ""
                break

        if full:
            st.session_state.messages.append({"role": "assistant", "content": full})
            persist_messages(st.session_state.messages, API_BASE)
            st.rerun()
