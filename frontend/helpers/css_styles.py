THINKING_STYLE = """
<style>
@keyframes thinkPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.55; transform: scale(0.98); }
}
.robot-pulse {
  display: inline-block;
  margin-right: 0.35rem;
  animation: thinkPulse 1.1s ease-in-out infinite;
}
.type-caret::after {
  content: "";
  display: inline-block;
  width: 0.12em;
  height: 1em;
  margin-left: 1px;
  background: currentColor;
  opacity: 0.85;
  animation: thinkPulse 0.8s ease-in-out infinite;
  vertical-align: text-bottom;
}
</style>
"""

# Chat bubbles: keep text top-aligned with the avatar and in a single column (no wrap under icon).
CHAT_BUBBLE_CSS = """
<style>
div[data-testid="stChatMessage"] {
  align-items: flex-start !important;
}
div[data-testid="stChatMessage"] > div:last-child {
  flex: 1 1 0% !important;
  min-width: 0 !important;
}
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
  margin-top: 0 !important;
  padding-top: 0 !important;
}
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p:first-child {
  margin-top: 0 !important;
}
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
  margin-bottom: 0.75em;
}
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p:last-child {
  margin-bottom: 0 !important;
}
</style>
"""

# Sidebar chat rows: left-aligned titles with ellipsis (Streamlit base buttons).
SIDEBAR_CHAT_LIST_CSS = """
<style>
section[data-testid="stSidebar"] button[data-testid^="stBaseButton"] {
  justify-content: flex-start !important;
  width: 100%;
}
section[data-testid="stSidebar"] button[data-testid^="stBaseButton"] > div {
  min-width: 0 !important;
  flex: 1 1 auto !important;
  justify-content: flex-start !important;
  overflow: hidden;
  width: 100%;
}
section[data-testid="stSidebar"] button[data-testid^="stBaseButton"] p {
  text-align: left !important;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
  min-width: 0;
  margin: 0 !important;
}
section[data-testid="stSidebar"] p.sidebar-chat-timestamp {
  text-align: right !important;
  margin: 0.15rem 0 0.65rem 0 !important;
  font-size: 0.875rem;
  color: rgba(49, 51, 63, 0.65);
}
</style>
"""
