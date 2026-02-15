"""
Notification Utilities Module

This module provides functions for sending various types of notifications
including event reminders, new research alerts, and submission status updates.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import and_

from models import db, User, Event, Research, NotificationLog


def log_notification(
    user_id: Optional[int],
    notification_type: str,
    recipient_email: str,
    subject: str,
    reference_id: Optional[int] = None,
    status: str = 'sent',
    error_message: Optional[str] = None
) -> NotificationLog:
    """
    Log a notification to the database.
    
    Args:
        user_id: User ID (can be None for bulk notifications)
        notification_type: Type of notification
        recipient_email: Email address sent to
        subject: Email subject
        reference_id: Optional reference ID (event_id, research_id, etc.)
        status: 'sent' or 'failed'
        error_message: Error details if failed
        
    Returns:
        NotificationLog: The created log entry
    """
    log = NotificationLog(
        user_id=user_id,
        notification_type=notification_type,
        reference_id=reference_id,
        recipient_email=recipient_email,
        subject=subject,
        status=status,
        error_message=error_message
    )
    db.session.add(log)
    db.session.commit()
    return log


def send_event_reminder(event, user=None, send_email_func=None) -> int:
    """
    Send event reminder notification to users.
    
    Args:
        event: Event model instance or event_id
        user: Optional specific user (if None, sends to all opted-in users)
        send_email_func: Optional email function to use
        
    Returns:
        int: Count of notifications sent
    """
    from utils.email_utils import send_event_reminder_email
    
    # Handle both Event object and ID
    if isinstance(event, int):
        event = Event.query.get(event)
        if not event:
            return 0
    
    count = 0
    
    if user:
        # Send to specific user
        if user.event_reminders_enabled:
            try:
                if send_email_func:
                    send_email_func(user, event)
                else:
                    send_event_reminder_email(user, event)
                
                log_notification(
                    user_id=user.id,
                    notification_type='event_reminder',
                    recipient_email=user.email,
                    subject=f"Reminder: {event.title} - PSRA Event",
                    reference_id=event.id,
                    status='sent'
                )
                count += 1
            except Exception as e:
                log_notification(
                    user_id=user.id,
                    notification_type='event_reminder',
                    recipient_email=user.email,
                    subject=f"Reminder: {event.title} - PSRA Event",
                    reference_id=event.id,
                    status='failed',
                    error_message=str(e)
                )
    else:
        # Send to all opted-in users
        users = User.query.filter_by(event_reminders_enabled=True).all()
        for u in users:
            try:
                if send_email_func:
                    send_email_func(u, event)
                else:
                    send_event_reminder_email(u, event)
                
                log_notification(
                    user_id=u.id,
                    notification_type='event_reminder',
                    recipient_email=u.email,
                    subject=f"Reminder: {event.title} - PSRA Event",
                    reference_id=event.id,
                    status='sent'
                )
                count += 1
            except Exception as e:
                log_notification(
                    user_id=u.id,
                    notification_type='event_reminder',
                    recipient_email=u.email,
                    subject=f"Reminder: {event.title} - PSRA Event",
                    reference_id=event.id,
                    status='failed',
                    error_message=str(e)
                )
    
    return count


def send_new_research_alert(research, send_email_func=None) -> int:
    """
    Send new research publication alert to opted-in users.
    
    Args:
        research: Research model instance or research_id
        send_email_func: Optional email function to use (receives user and research)
        
    Returns:
        int: Count of notifications sent
    """
    from utils.email_utils import send_new_research_email
    
    # Handle both Research object and ID
    if isinstance(research, int):
        research = Research.query.get(research)
        if not research:
            return 0
    
    count = 0
    
    # Send to all opted-in users
    users = User.query.filter_by(new_research_alerts_enabled=True).all()
    
    for user in users:
        try:
            if send_email_func:
                send_email_func(user, research)
            else:
                send_new_research_email(user, research)
            
            log_notification(
                user_id=user.id,
                notification_type='new_research',
                recipient_email=user.email,
                subject=f"New Research: {research.title[:50]}...",
                reference_id=research.id,
                status='sent'
            )
            count += 1
        except Exception as e:
            log_notification(
                user_id=user.id,
                notification_type='new_research',
                recipient_email=user.email,
                subject=f"New Research: {research.title[:50]}...",
                reference_id=research.id,
                status='failed',
                error_message=str(e)
            )
    
    return count


def send_research_approved_notification(user, research, send_email_func=None) -> bool:
    """
    Send notification when research submission is approved.
    
    Args:
        user: User model instance (the submitter)
        research: Research model instance
        send_email_func: Optional email function to use
        
    Returns:
        bool: True if notification was sent, False otherwise
    """
    from utils.email_utils import send_research_status_email
    
    if not user or not user.email_notifications_enabled:
        return False
    
    try:
        if send_email_func:
            send_email_func(user, research, 'approved')
        else:
            send_research_status_email(user, research, 'approved')
        
        log_notification(
            user_id=user.id,
            notification_type='research_status',
            recipient_email=user.email,
            subject="Your Research Submission Has Been Approved",
            reference_id=research.id if hasattr(research, 'id') else None,
            status='sent'
        )
        return True
    except Exception as e:
        log_notification(
            user_id=user.id,
            notification_type='research_status',
            recipient_email=user.email,
            subject="Your Research Submission Has Been Approved",
            reference_id=research.id if hasattr(research, 'id') else None,
            status='failed',
            error_message=str(e)
        )
        return False


def send_research_rejected_notification(user, research_title, reason=None, send_email_func=None) -> bool:
    """
    Send notification when research submission is rejected.
    
    Args:
        user: User model instance (the submitter)
        research_title: Title of the rejected research
        reason: Optional reason for rejection
        send_email_func: Optional email function to use
        
    Returns:
        bool: True if notification was sent, False otherwise
    """
    from utils.email_utils import send_research_status_email
    
    if not user or not user.email_notifications_enabled:
        return False
    
    subject = "Your Research Submission Has Been Rejected"
    
    try:
        if send_email_func:
            # Create a minimal dict-like object for the research
            research_dict = {'title': research_title, 'author_name': ''}
            send_email_func(user, research_dict, 'rejected', reason)
        else:
            research_dict = {'title': research_title, 'author_name': ''}
            send_research_status_email(user, research_dict, 'rejected', reason)
        
        log_notification(
            user_id=user.id,
            notification_type='research_status',
            recipient_email=user.email,
            subject=subject,
            status='sent'
        )
        return True
    except Exception as e:
        log_notification(
            user_id=user.id,
            notification_type='research_status',
            recipient_email=user.email,
            subject=subject,
            status='failed',
            error_message=str(e)
        )
        return False


def get_upcoming_events_for_reminder(days_ahead: int = 1) -> List[Event]:
    """
    Get events happening within the specified number of days.
    
    Args:
        days_ahead: Number of days to look ahead
        
    Returns:
        list: List of Event objects
    """
    now = datetime.utcnow()
    end_date = now + timedelta(days=days_ahead)
    
    return Event.query.filter(
        and_(
            Event.event_date >= now.date(),
            Event.event_date <= end_date.date()
        )
    ).all()


def send_scheduled_event_reminders(send_email_func=None) -> int:
    """
    Send reminders for events happening tomorrow.
    This is intended to be run as a scheduled task.
    
    Args:
        send_email_func: Optional email function to use
        
    Returns:
        int: Total count of notifications sent
    """
    events = get_upcoming_events_for_reminder(days_ahead=1)
    
    total_sent = 0
    
    for event in events:
        count = send_event_reminder(event, send_email_func=send_email_func)
        total_sent += count
    
    return total_sent


def get_notification_history(user_id: Optional[int] = None, limit: int = 50) -> List[NotificationLog]:
    """
    Get notification history.
    
    Args:
        user_id: Optional user ID to filter by
        limit: Maximum number of records to return
        
    Returns:
        list: List of NotificationLog objects
    """
    query = NotificationLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    return query.order_by(NotificationLog.sent_at.desc()).limit(limit).all()


def get_notification_stats() -> Dict[str, Any]:
    """
    Get notification statistics.
    
    Returns:
        dict: Dictionary with notification statistics
    """
    total_sent = NotificationLog.query.filter_by(status='sent').count()
    total_failed = NotificationLog.query.filter_by(status='failed').count()
    
    # By type
    type_stats = db.session.query(
        NotificationLog.notification_type,
        db.func.count(NotificationLog.id)
    ).group_by(NotificationLog.notification_type).all()
    
    return {
        'total_sent': total_sent,
        'total_failed': total_failed,
        'by_type': dict(type_stats)
    }