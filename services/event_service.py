"""
Event Service Module

Business logic for event management functionality.
"""

from datetime import datetime, date, time
from typing import Dict, List, Optional, Tuple

from models import db, Event


class EventService:
    """Service class for event-related operations."""
    
    @staticmethod
    def get_categorized_events() -> Dict[str, List[Event]]:
        """
        Get events categorized by status (live, upcoming, archived).
        
        Also automatically archives past events.
        
        Returns:
            Dictionary with 'live', 'upcoming', and 'archived' event lists
        """
        today = date.today()
        now = datetime.now().time()
        
        # Archive past events automatically
        EventService.archive_past_events(today, now)
        
        # Get live events (today with future times)
        live_events = Event.query.filter(
            (Event.event_date == today) & 
            (Event.event_time > now) & 
            (Event.event_time.isnot(None))
        ).filter(Event.is_archived == False).order_by(Event.event_time.asc()).all()
        
        # Get upcoming events (future dates)
        upcoming_events = Event.query.filter(
            Event.event_date > today
        ).filter(Event.is_archived == False).order_by(
            Event.event_date.asc(), 
            Event.event_time.asc()
        ).all()
        
        # Get archived events
        archived_events = Event.query.filter(
            Event.is_archived == True
        ).order_by(Event.event_date.desc(), Event.event_time.desc()).all()
        
        return {
            'live': live_events,
            'upcoming': upcoming_events,
            'archived': archived_events
        }
    
    @staticmethod
    def archive_past_events(today: date, now: time) -> int:
        """
        Automatically archive events that have passed.
        
        Args:
            today: Current date
            now: Current time
        
        Returns:
            Number of events archived
        """
        past_events = Event.query.filter(
            (Event.event_date < today) |
            ((Event.event_date == today) & (Event.event_time <= now) & (Event.event_time.isnot(None)))
        ).filter(Event.is_archived == False).all()
        
        count = 0
        for event in past_events:
            event.is_archived = True
            count += 1
        
        if count > 0:
            db.session.commit()
        
        return count
    
    @staticmethod
    def get_next_event() -> Optional[Event]:
        """
        Get the next upcoming event.
        
        Returns:
            The next event or None if no upcoming events
        """
        today = date.today()
        now = datetime.now().time()
        
        return Event.query.filter(
            (Event.event_date > today) |
            ((Event.event_date == today) & (Event.event_time > now) & (Event.event_time.isnot(None)))
        ).filter(Event.is_archived == False).order_by(
            Event.event_date.asc(), 
            Event.event_time.asc()
        ).first()
    
    @staticmethod
    def get_event_data(event: Event) -> Dict:
        """
        Get event data formatted for JSON response.
        
        Args:
            event: Event instance
        
        Returns:
            Dictionary with event data
        """
        event_datetime = None
        if event.event_time:
            event_datetime = datetime.combine(event.event_date, event.event_time)
        else:
            event_datetime = datetime.combine(event.event_date, datetime.min.time())
        
        return {
            'title': event.title,
            'description': event.description,
            'event_datetime': event_datetime.isoformat(),
            'has_time': event.event_time is not None,
            'image_url': event.image_url
        }
    
    @staticmethod
    def create_event(
        title: str,
        event_date: date,
        created_by: int,
        description: Optional[str] = None,
        event_time: Optional[time] = None,
        presenter: Optional[str] = None,
        event_url: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Event:
        """
        Create a new event.
        
        Args:
            title: Event title
            event_date: Event date
            created_by: User ID of creator
            description: Optional description
            event_time: Optional event time
            presenter: Optional presenter name
            event_url: Optional event URL
            image_url: Optional image URL
        
        Returns:
            The created Event instance
        """
        event = Event(
            title=title,
            description=description,
            event_date=event_date,
            event_time=event_time,
            image_url=image_url,
            presenter=presenter,
            event_url=event_url,
            created_by=created_by
        )
        db.session.add(event)
        db.session.commit()
        return event
    
    @staticmethod
    def update_event(event: Event, **kwargs) -> Event:
        """
        Update an event with provided fields.
        
        Args:
            event: Event instance to update
            **kwargs: Fields to update
        
        Returns:
            The updated Event instance
        """
        for key, value in kwargs.items():
            if hasattr(event, key) and value is not None:
                setattr(event, key, value)
        
        db.session.commit()
        return event
    
    @staticmethod
    def delete_event(event: Event) -> bool:
        """
        Delete an event.
        
        Args:
            event: Event instance to delete
        
        Returns:
            True if successful
        """
        db.session.delete(event)
        db.session.commit()
        return True
    
    @staticmethod
    def parse_event_date(date_string: str) -> date:
        """
        Parse a date string in YYYY-MM-DD format.
        
        Args:
            date_string: Date string to parse
        
        Returns:
            date object
        """
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    
    @staticmethod
    def parse_event_time(time_string: Optional[str]) -> Optional[time]:
        """
        Parse a time string in HH:MM format.
        
        Args:
            time_string: Time string to parse (can be None)
        
        Returns:
            time object or None
        """
        if time_string:
            return datetime.strptime(time_string, '%H:%M').time()
        return None
