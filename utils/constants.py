"""
Application Constants Module

Centralizes all application constants, enums, and configuration values
to avoid magic strings and numbers throughout the codebase.
"""

# User status options
USER_STATUS_STUDENT = 'student'
USER_STATUS_ALUMNI = 'alumni'
USER_STATUS_UNDERGRADUATE = 'undergraduate'
USER_STATUSES = [USER_STATUS_STUDENT, USER_STATUS_ALUMNI, USER_STATUS_UNDERGRADUATE]

# Post categories for forum
POST_CATEGORIES = [
    ('Pharmacology', 'Pharmacology'),
    ('Clinical Pharmacy', 'Clinical Pharmacy'),
    ('Research Skills', 'Research Skills')
]

# Pagination defaults
DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 100

# Batch number range (for pharmacy students)
MIN_BATCH_NUMBER = 1
MAX_BATCH_NUMBER = 58

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
