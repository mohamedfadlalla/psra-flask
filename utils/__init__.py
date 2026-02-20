"""
Utils Package

Utility modules for the PSRA application.
"""

from .json_utils import safe_json_parse, combine_timeline, get_user_timeline
from .image_utils import (
    process_image,
    process_profile_picture,
    save_event_image,
    delete_file,
    get_event_image_path
)
from .query_helpers import (
    get_conversation_messages,
    get_unread_message_count,
    paginate_query,
    search_query,
    get_or_404,
    get_latest_message,
    get_conversation_participants,
    delete_conversation_messages
)
from .constants import (
    USER_STATUS_STUDENT,
    USER_STATUS_ALUMNI,
    USER_STATUS_UNDERGRADUATE,
    USER_STATUSES,
    POST_CATEGORIES,
    DEFAULT_PER_PAGE,
    MAX_PER_PAGE,
    FLASH_SUCCESS,
    FLASH_ERROR,
    FLASH_WARNING,
    FLASH_INFO
)
from .decorators import admin_required, anonymous_required, owner_required

__all__ = [
    # JSON utilities
    'safe_json_parse',
    'combine_timeline',
    'get_user_timeline',
    # Image utilities
    'process_image',
    'process_profile_picture',
    'save_event_image',
    'delete_file',
    'get_event_image_path',
    # Query helpers
    'get_conversation_messages',
    'get_unread_message_count',
    'paginate_query',
    'search_query',
    'get_or_404',
    'get_latest_message',
    'get_conversation_participants',
    'delete_conversation_messages',
    # Constants
    'USER_STATUS_STUDENT',
    'USER_STATUS_ALUMNI',
    'USER_STATUS_UNDERGRADUATE',
    'USER_STATUSES',
    'POST_CATEGORIES',
    'DEFAULT_PER_PAGE',
    'MAX_PER_PAGE',
    'FLASH_SUCCESS',
    'FLASH_ERROR',
    'FLASH_WARNING',
    'FLASH_INFO',
    # Decorators
    'admin_required',
    'anonymous_required',
    'owner_required'
]
