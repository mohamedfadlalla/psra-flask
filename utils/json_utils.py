"""
JSON Utilities Module

Provides safe JSON parsing and data transformation utilities
to reduce duplicate code across the application.
"""

import json
from typing import Any, List, Dict, Optional


def safe_json_parse(json_string: Optional[str], default: Any = None) -> Any:
    """
    Safely parse a JSON string with a fallback default value.
    
    Args:
        json_string: The JSON string to parse, can be None or empty
        default: The default value to return if parsing fails (defaults to empty list)
    
    Returns:
        The parsed JSON data or the default value if parsing fails
    
    Examples:
        >>> safe_json_parse('["a", "b"]')
        ['a', 'b']
        >>> safe_json_parse(None)
        []
        >>> safe_json_parse('invalid json', default={})
        {}
    """
    if default is None:
        default = []
    
    if not json_string:
        return default
    
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def combine_timeline(experience_data: List[Dict], education_data: List[Dict]) -> List[Dict]:
    """
    Combine experience and education entries into a single chronological timeline.
    
    Args:
        experience_data: List of work experience entries
        education_data: List of education entries
    
    Returns:
        Combined list sorted by start_date descending (most recent first)
    
    Examples:
        >>> exp = [{'title': 'Developer', 'start_date': '2020-01'}]
        >>> edu = [{'school': 'University', 'start_date': '2016-09', 'type': 'education'}]
        >>> combine_timeline(exp, edu)
        [{'title': 'Developer', 'start_date': '2020-01', 'type': 'work'}, ...]
    """
    combined = []
    
    for entry in experience_data:
        entry_copy = entry.copy()
        entry_copy['type'] = 'work'
        combined.append(entry_copy)
    
    for entry in education_data:
        entry_copy = entry.copy()
        entry_copy['type'] = 'education'
        combined.append(entry_copy)
    
    # Sort by start_date descending (most recent first)
    combined.sort(key=lambda x: x.get('start_date', ''), reverse=True)
    
    return combined


def get_user_timeline(user) -> List[Dict]:
    """
    Get combined experience/education timeline for a user.
    
    Args:
        user: User model instance with experience and education JSON fields
    
    Returns:
        Combined and sorted timeline list
    """
    experience_entries = safe_json_parse(user.experience)
    education_entries = safe_json_parse(user.education)
    return combine_timeline(experience_entries, education_entries)
