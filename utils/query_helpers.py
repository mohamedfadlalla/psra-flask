"""
Query Helpers Module

Provides common database query patterns to reduce duplicate code
across the application.
"""

from typing import List, Optional, Type, TypeVar
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query

T = TypeVar('T')


def get_conversation_messages(db: SQLAlchemy, Message, user_id: int, other_user_id: int) -> List:
    """
    Get all messages between two users.
    
    Args:
        db: SQLAlchemy database instance
        Message: Message model class
        user_id: First user's ID
        other_user_id: Second user's ID
    
    Returns:
        List of messages between the two users
    """
    return Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
    )


def get_unread_message_count(Message, user_id: int, from_user_id: Optional[int] = None) -> int:
    """
    Get the count of unread messages for a user.
    
    Args:
        Message: Message model class
        user_id: The user's ID (receiver)
        from_user_id: Optional sender ID to filter by
    
    Returns:
        Count of unread messages
    """
    query = Message.query.filter_by(receiver_id=user_id, is_read=False)
    if from_user_id:
        query = query.filter_by(sender_id=from_user_id)
    return query.count()


def paginate_query(query: Query, page: int, per_page: int = 20, error_out: bool = False):
    """
    Apply pagination to a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        per_page: Number of items per page
        error_out: Whether to raise 404 on invalid page
    
    Returns:
        Pagination object with items, pages, total, etc.
    """
    return query.paginate(page=page, per_page=per_page, error_out=error_out)


def search_query(query: Query, model, search_term: str, *fields) -> Query:
    """
    Apply a search filter to a query across multiple fields.
    
    Args:
        query: SQLAlchemy query object
        model: The model class being queried
        search_term: The search term to look for
        *fields: Field names to search in
    
    Returns:
        Filtered query object
    """
    if not search_term:
        return query
    
    filters = []
    for field in fields:
        field_attr = getattr(model, field, None)
        if field_attr is not None:
            filters.append(field_attr.contains(search_term))
    
    if filters:
        from sqlalchemy import or_
        query = query.filter(or_(*filters))
    
    return query


def get_or_404(model: Type[T], item_id: int) -> T:
    """
    Get a model instance by ID or raise 404.
    
    Args:
        model: The model class
        item_id: The item's ID
    
    Returns:
        The model instance
    
    Raises:
        404 error if not found
    """
    return model.query.get_or_404(item_id)


def get_latest_message(Message, user_id: int, other_user_id: int):
    """
    Get the latest message between two users.
    
    Args:
        Message: Message model class
        user_id: First user's ID
        other_user_id: Second user's ID
    
    Returns:
        The most recent message or None
    """
    return Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
    ).order_by(Message.created_at.desc()).first()


def get_conversation_participants(Message, user_id: int) -> List[int]:
    """
    Get all user IDs that have exchanged messages with a user.
    
    Args:
        Message: Message model class
        user_id: The user's ID
    
    Returns:
        Set of user IDs who have conversations with this user
    """
    sent = Message.query.filter_by(sender_id=user_id).with_entities(Message.receiver_id).all()
    received = Message.query.filter_by(receiver_id=user_id).with_entities(Message.sender_id).all()
    
    user_ids = set()
    for msg in sent:
        user_ids.add(msg.receiver_id)
    for msg in received:
        user_ids.add(msg.sender_id)
    
    return user_ids


def delete_conversation_messages(db: SQLAlchemy, Message, user_id: int, other_user_id: int) -> int:
    """
    Delete all messages between two users.
    
    Args:
        db: SQLAlchemy database instance
        Message: Message model class
        user_id: First user's ID
        other_user_id: Second user's ID
    
    Returns:
        Number of deleted messages
    """
    result = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
    ).delete()
    db.session.commit()
    return result
