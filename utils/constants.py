"""
Application Constants Module

Centralizes all application constants, enums, and configuration values
to avoid magic strings and numbers throughout the codebase.
"""

# Pagination defaults
DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 100

# Profile image settings
PROFILE_PICTURE_SIZE = (150, 150)
COVER_PHOTO_SIZE = (1200, 400)
MAX_IMAGE_SIZE_MB = 5

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Message settings
MAX_MESSAGE_LENGTH = 1000

# Flash message categories
FLASH_SUCCESS = 'success'
FLASH_ERROR = 'error'
FLASH_WARNING = 'warning'
FLASH_INFO = 'info'

# Email settings
EMAIL_BATCH_SIZE = 50

# Event status
EVENT_STATUS_LIVE = 'live'
EVENT_STATUS_UPCOMING = 'upcoming'
EVENT_STATUS_ARCHIVED = 'archived'
