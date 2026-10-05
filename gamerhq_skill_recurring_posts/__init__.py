from .skill import (
    CREATE_API,
    DESCRIBE_API,
    DELETE_API,
    DELETE_PREVIEW_API,
    GET_API,
    HANDLER_ID,
    LIST_API,
    MAX_POSTS,
    MIN_INTERVAL_SECONDS,
    MAX_CONTENT_CHARS,
    MAX_NAME_CHARS,
    SENT_EVENT_ID,
    SET_ACTIVE_API,
    UPDATE_API,
    VALIDATE_API,
    SKILL_ID,
    STORAGE_KEY,
    RecurringPost,
    RecurringPostsSkill,
)


def create_skill():
    return RecurringPostsSkill()


__all__ = [
    "CREATE_API",
    "DESCRIBE_API",
    "DELETE_API",
    "DELETE_PREVIEW_API",
    "GET_API",
    "HANDLER_ID",
    "LIST_API",
    "MAX_POSTS",
    "MIN_INTERVAL_SECONDS",
    "MAX_CONTENT_CHARS",
    "MAX_NAME_CHARS",
    "SENT_EVENT_ID",
    "SET_ACTIVE_API",
    "UPDATE_API",
    "VALIDATE_API",
    "SKILL_ID",
    "STORAGE_KEY",
    "RecurringPost",
    "RecurringPostsSkill",
    "create_skill",
]
