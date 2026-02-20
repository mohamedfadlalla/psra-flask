"""
Message Service Module

Business logic for messaging functionality.
"""

from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

from models import db, User, Message
from utils.query_helpers import (
    get_conversation_participants,
    get_latest_message,
    get_unread_message_count
)


class MessageService:
    """Service class for message-related operations."""
    
    @staticmethod
    def get_conversations(user_id: int) -> List[Dict]:
        """
        Get all conversations for a user with latest message and unread count.
        
        Args:
            user_id: The user's ID
        
        Returns:
            List of conversation dictionaries sorted by latest message
        """
        # Get all user IDs who have exchanged messages with this user
        participant_ids = get_conversation_participants(Message, user_id)
        
        conversations = []
        for other_user_id in participant_ids:
            other_user = User.query.get(other_user_id)
            if not other_user:
                continue
            
            # Get latest message
            latest_message = get_latest_message(Message, user_id, other_user_id)
            
            # Count unread messages from this user
            unread_count = get_unread_message_count(Message, user_id, other_user_id)
            
            conversations.append({
                'user': other_user,
                'latest_message': latest_message,
                'unread_count': unread_count
            })
        
        # Sort by latest message timestamp
        conversations.sort(
            key=lambda x: x['latest_message'].created_at if x['latest_message'] else datetime.min,
            reverse=True
        )
        
        return conversations
    
    @staticmethod
    def get_conversation_messages(user_id: int, other_user_id: int) -> List[Message]:
        """
        Get all messages between two users.
        
        Args:
            user_id: First user's ID
            other_user_id: Second user's ID
        
        Returns:
            List of messages ordered by creation time
        """
        return Message.query.filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id)) |
            ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
        ).order_by(Message.created_at.asc()).all()
    
    @staticmethod
    def get_grouped_messages(user_id: int, other_user_id: int) -> List[Tuple]:
        """
        Get messages grouped by date for display.
        
        Args:
            user_id: First user's ID
            other_user_id: Second user's ID
        
        Returns:
            List of (date, messages) tuples
        """
        messages = MessageService.get_conversation_messages(user_id, other_user_id)
        
        # Group messages by date
        messages_by_date = defaultdict(list)
        for message in messages:
            date_key = message.created_at.date()
            messages_by_date[date_key].append(message)
        
        # Convert to sorted list of tuples
        grouped_messages = []
        for date_key in sorted(messages_by_date.keys()):
            grouped_messages.append((date_key, messages_by_date[date_key]))
        
        return grouped_messages
    
    @staticmethod
    def get_or_create_conversation(user_id1: int, user_id2: int) -> int:
        """Get existing or create a new conversation for two users."""
        from models import Conversation, ConversationParticipant
        cp1_alias = db.aliased(ConversationParticipant)
        cp2_alias = db.aliased(ConversationParticipant)
        
        existing = db.session.query(Conversation.id).join(
            cp1_alias, Conversation.id == cp1_alias.conversation_id
        ).join(
            cp2_alias, Conversation.id == cp2_alias.conversation_id
        ).filter(
            cp1_alias.user_id == user_id1,
            cp2_alias.user_id == user_id2
        ).first()
        
        if existing:
            return existing[0]
            
        conv = Conversation()
        db.session.add(conv)
        db.session.flush()
        
        cp1 = ConversationParticipant(conversation_id=conv.id, user_id=user_id1)
        cp2 = ConversationParticipant(conversation_id=conv.id, user_id=user_id2)
        db.session.add_all([cp1, cp2])
        db.session.flush()
        
        return conv.id

    @staticmethod
    def send_message(sender_id: int, receiver_id: int, content: str) -> Message:
        """
        Send a message from one user to another.
        
        Args:
            sender_id: Sender's user ID
            receiver_id: Receiver's user ID
            content: Message content
        
        Returns:
            The created Message instance
        """
        conv_id = MessageService.get_or_create_conversation(sender_id, receiver_id)
        
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            conversation_id=conv_id,
            content=content
        )
        db.session.add(message)
        db.session.commit()
        return message
    
    @staticmethod
    def mark_messages_as_read(user_id: int, other_user_id: int) -> int:
        """
        Mark all unread messages from other_user as read.
        
        Args:
            user_id: The current user's ID (receiver)
            other_user_id: The conversation partner's ID (sender)
        
        Returns:
            Number of messages marked as read
        """
        unread_messages = Message.query.filter_by(
            sender_id=other_user_id,
            receiver_id=user_id,
            is_read=False
        ).all()
        
        count = 0
        for message in unread_messages:
            message.is_read = True
            message.read_at = datetime.utcnow()
            count += 1
        
        if count > 0:
            db.session.commit()
        
        return count
    
    @staticmethod
    def delete_message(message_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Delete a message (only if user owns it).
        
        Args:
            message_id: The message ID to delete
            user_id: The requesting user's ID
        
        Returns:
            Tuple of (success, error_message)
        """
        message = Message.query.get(message_id)
        if not message:
            return False, 'Message not found'
        
        if message.sender_id != user_id:
            return False, 'You can only delete your own messages'
        
        db.session.delete(message)
        db.session.commit()
        return True, ''
    
    @staticmethod
    def delete_conversation(user_id: int, other_user_id: int) -> int:
        """
        Delete all messages between two users.
        
        Args:
            user_id: First user's ID
            other_user_id: Second user's ID
        
        Returns:
            Number of deleted messages
        """
        count = Message.query.filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id)) |
            ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
        ).delete()
        db.session.commit()
        return count
    
    @staticmethod
    def get_message_data(message: Message) -> Dict:
        """
        Get message data formatted for JSON response.
        
        Args:
            message: Message instance
        
        Returns:
            Dictionary with message data
        """
        return {
            'id': message.id,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'content': message.content,
            'is_read': message.is_read,
            'read_at': message.read_at.isoformat() if message.read_at else None,
            'created_at': message.created_at.isoformat(),
            'sender_name': message.sender.name
        }
