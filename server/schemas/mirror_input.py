from typing import Literal

from pydantic import BaseModel


class MirrorInput(BaseModel):
    content: str
    content_type: Literal[
        "chat_log",
        "meeting_notes",
        "email_thread",
        "requirement_doc",
        "self_check",
        "free_text",
    ] = "free_text"
    language: Literal["zh", "en", "auto"] = "auto"
    trigger_mode: Literal[
        "manual",
        "bot_mention",
        "self_mirror",
        "event_trigger",
        "always_on",
    ] = "manual"
    anonymous_mode: bool = True
    analysis_focus: list[Literal["communication", "behavior", "structural"]] | None = None
