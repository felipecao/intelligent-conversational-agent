WAITING_MESSAGES = (
    "thinking...",
    "searching knowledge base...",
    "looking into the mysteries of the universe...",
)


def thinking_html(typed: str) -> str:
    """Robot + typewriter line; pulse on the robot (spinner-like)."""
    safe = typed.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<p style="margin:0;">
  <span class="robot-pulse" aria-hidden="true">🤖</span>
  <em class="type-caret" style="white-space:pre-wrap;">{safe}</em>
</p>"""
