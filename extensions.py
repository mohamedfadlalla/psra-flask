"""
Extensions Module

Initialize Flask extensions to avoid circular imports.
"""

from authlib.integrations.flask_client import OAuth

oauth = OAuth()