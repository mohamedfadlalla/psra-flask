from flask import current_app, render_template_string
from flask_mail import Message
from models import User
import logging


def is_mail_configured():
    """
    Check if mail is properly configured.
    
    Returns:
        tuple: (is_configured: bool, error_message: str or None)
    """
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    mail_server = current_app.config.get('MAIL_SERVER')
    
    missing = []
    if not mail_server:
        missing.append('MAIL_SERVER')
    if not mail_username:
        missing.append('MAIL_USERNAME')
    if not mail_password:
        missing.append('MAIL_PASSWORD')
    
    if missing:
        return False, f"Missing mail configuration: {', '.join(missing)}"
    
    return True, None


def send_email(subject, recipients, html_body, text_body=None):
    """
    Send an email using Flask-Mail with error handling.

    Args:
        subject (str): Email subject
        recipients (list): List of recipient email addresses
        html_body (str): HTML content of the email
        text_body (str, optional): Plain text version of the email

    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    is_configured, config_error = is_mail_configured()
    if not is_configured:
        current_app.logger.error(f"Email not sent - {config_error}")
        return False, config_error
    
    if not recipients:
        error_msg = "No recipients provided"
        current_app.logger.warning(f"Email not sent - {error_msg}")
        return False, error_msg
    
    try:
        sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')

        msg = Message(
            subject=subject,
            sender=sender,
            recipients=recipients,
            html=html_body
        )

        if text_body:
            msg.body = text_body

        current_app.extensions['mail'].send(msg)
        current_app.logger.info(f"Email sent successfully to {len(recipients)} recipients: {subject}")
        return True, None

    except Exception as e:
        error_msg = str(e)
        current_app.logger.error(f"Failed to send email: {error_msg}")
        return False, error_msg

def send_event_notification(event):
    """
    Send event notification email to all users.

    Args:
        event: Event model instance

    Returns:
        tuple: (success_count, failure_count)
    """
    # Get all users with valid email addresses
    users = User.query.filter(User.email.isnot(None)).all()

    if not users:
        logging.warning("No users found with email addresses for event notification")
        return 0, 0

    # Prepare event details
    event_date_str = event.event_date.strftime('%B %d, %Y')
    event_time_str = event.event_time.strftime('%I:%M %p') if event.event_time else 'TBD'

    # Create email content
    subject = f"New Event: {event.title}"

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #007bff; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background-color: #f9f9f9; }
            .event-details { background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
            .event-title { font-size: 24px; font-weight: bold; color: #007bff; margin-bottom: 10px; }
            .event-info { margin: 5px 0; }
            .event-label { font-weight: bold; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>PSRA Event Notification</h1>
            </div>
            <div class="content">
                <p>Dear PSRA Community Member,</p>

                <p>We're excited to announce a new event that has been added to our calendar!</p>

                <div class="event-details">
                    <div class="event-title">{{ event.title }}</div>

                    {% if event.description %}
                    <div class="event-info">
                        <span class="event-label">Description:</span><br>
                        {{ event.description }}
                    </div>
                    {% endif %}

                    <div class="event-info">
                        <span class="event-label">Date:</span> {{ event_date_str }}
                    </div>

                    <div class="event-info">
                        <span class="event-label">Time:</span> {{ event_time_str }}
                    </div>

                    {% if event.presenter %}
                    <div class="event-info">
                        <span class="event-label">Presenter:</span> {{ event.presenter }}
                    </div>
                    {% endif %}

                    {% if event.event_url %}
                    <div class="event-info">
                        <span class="event-label">Event Link:</span> <a href="{{ event.event_url }}" target="_blank">{{ event.event_url }}</a>
                    </div>
                    {% endif %}
                </div>

                <p>Don't miss out on this exciting opportunity! Visit our events page to learn more and register if required.</p>

                <p>Best regards,<br>
                PSRA Team</p>
            </div>
            <div class="footer">
                <p>This is an automated notification from the PSRA website.</p>
                <p>If you no longer wish to receive these notifications, please contact us.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Render the HTML template
    html_body = render_template_string(html_template,
                                     event=event,
                                     event_date_str=event_date_str,
                                     event_time_str=event_time_str)

    # Create text version
    text_body = f"""
    PSRA Event Notification

    New Event: {event.title}

    Date: {event_date_str}
    Time: {event_time_str}
    """

    if event.presenter:
        text_body += f"Presenter: {event.presenter}\n"

    if event.description:
        text_body += f"\nDescription: {event.description}\n"

    if event.event_url:
        text_body += f"\nEvent Link: {event.event_url}\n"

    text_body += "\nVisit our events page to learn more!\n\nBest regards,\nPSRA Team"

    # Send emails in batches to avoid overwhelming the mail server
    success_count = 0
    failure_count = 0
    batch_size = 50

    for i in range(0, len(users), batch_size):
        batch_users = users[i:i + batch_size]
        batch_emails = [user.email for user in batch_users if user.email]

        if batch_emails:
            success, error = send_email(subject, batch_emails, html_body, text_body)
            if success:
                success_count += len(batch_emails)
            else:
                failure_count += len(batch_emails)

    current_app.logger.info(f"Event notification sent: {success_count} successful, {failure_count} failed")
    return success_count, failure_count


def send_event_reminder_email(user, event):
    """
    Send an event reminder email to a user.
    
    Args:
        user: User model instance
        event: Event model instance
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    event_date_str = event.event_date.strftime('%B %d, %Y')
    event_time_str = event.event_time.strftime('%I:%M %p') if event.event_time else 'TBD'
    
    subject = f"Reminder: {event.title} - PSRA Event"
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #667eea; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background-color: #f9f9f9; }
            .event-details { background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
            .event-title { font-size: 24px; font-weight: bold; color: #667eea; margin-bottom: 10px; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Event Reminder</h1>
            </div>
            <div class="content">
                <p>Dear {{ user.name }},</p>
                
                <p>This is a reminder that the following event is happening soon:</p>
                
                <div class="event-details">
                    <div class="event-title">{{ event.title }}</div>
                    <p><strong>Date:</strong> {{ event_date_str }}</p>
                    <p><strong>Time:</strong> {{ event_time_str }}</p>
                    {% if event.presenter %}
                    <p><strong>Presenter:</strong> {{ event.presenter }}</p>
                    {% endif %}
                    {% if event.event_url %}
                    <p><strong>Link:</strong> <a href="{{ event.event_url }}">Join Event</a></p>
                    {% endif %}
                </div>
                
                <p>Best regards,<br>PSRA Team</p>
            </div>
            <div class="footer">
                <p>This is an automated notification from the PSRA website.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_body = render_template_string(html_template, user=user, event=event, 
                                        event_date_str=event_date_str, event_time_str=event_time_str)
    
    return send_email(subject, [user.email], html_body)


def send_new_research_email(user, research):
    """
    Send a new research publication notification email.
    
    Args:
        user: User model instance
        research: Research model instance
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = f"New Research: {research.title[:50]}... - PSRA"
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #667eea; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background-color: #f9f9f9; }
            .research-details { background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
            .research-title { font-size: 20px; font-weight: bold; color: #667eea; margin-bottom: 10px; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>New Research Publication</h1>
            </div>
            <div class="content">
                <p>Dear {{ user.name }},</p>
                
                <p>A new research publication has been added to our database:</p>
                
                <div class="research-details">
                    <div class="research-title">{{ research.title }}</div>
                    <p><strong>Author:</strong> {{ research.author.name }}</p>
                    <p><strong>Department:</strong> {{ research.department }}</p>
                    <p><strong>Year:</strong> {{ research.year }}</p>
                    {% if research.doi_url %}
                    <p><strong>Link:</strong> <a href="{{ research.doi_url }}">View Publication</a></p>
                    {% endif %}
                </div>
                
                <p>Visit our website to explore more research publications.</p>
                
                <p>Best regards,<br>PSRA Team</p>
            </div>
            <div class="footer">
                <p>This is an automated notification from the PSRA website.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_body = render_template_string(html_template, user=user, research=research)
    
    return send_email(subject, [user.email], html_body)


def send_announcement_email(announcement, recipients):
    """
    Send an announcement email to a list of recipients.
    
    Args:
        announcement: Announcement model instance
        recipients: List of User model instances
        
    Returns:
        tuple: (success_count, failure_count, first_error_message)
    """
    if not recipients:
        current_app.logger.warning("No recipients for announcement")
        return 0, 0, "No recipients found"
    
    is_configured, config_error = is_mail_configured()
    if not is_configured:
        current_app.logger.error(f"Announcement not sent - {config_error}")
        return 0, len(recipients), config_error
    
    subject = f"[PSRA Announcement] {announcement.subject}"
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #2D577B; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background-color: #f9f9f9; }
            .announcement-body { background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; white-space: pre-wrap; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>PSRA Announcement</h1>
            </div>
            <div class="content">
                <p>Dear PSRA Community Member,</p>
                
                <div class="announcement-body">{{ body }}</div>
                
                <p>Best regards,<br>PSRA Team</p>
            </div>
            <div class="footer">
                <p>This is an announcement from the Pharmaceutical Studies and Research Association.</p>
                <p>If you no longer wish to receive these notifications, please update your preferences in your profile.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_body = render_template_string(html_template, body=announcement.body)
    
    text_body = f"""
PSRA Announcement

{announcement.body}

Best regards,
PSRA Team
"""
    
    success_count = 0
    failure_count = 0
    first_error = None
    batch_size = 50
    
    for i in range(0, len(recipients), batch_size):
        batch_recipients = recipients[i:i + batch_size]
        batch_emails = [user.email for user in batch_recipients if user.email]
        
        if batch_emails:
            success, error = send_email(subject, batch_emails, html_body, text_body)
            if success:
                success_count += len(batch_emails)
            else:
                failure_count += len(batch_emails)
                if first_error is None:
                    first_error = error
    
    current_app.logger.info(f"Announcement sent: {success_count} successful, {failure_count} failed")
    return success_count, failure_count, first_error


def send_research_status_email(user, research, status, reason=None):
    """
    Send a research submission status update email.
    
    Args:
        user: User model instance
        research: Research model instance (or dict with title and author name)
        status: 'approved' or 'rejected'
        reason: Optional reason for rejection
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if status == 'approved':
        subject = "Your Research Submission Has Been Approved - PSRA"
        status_color = "#28a745"
        status_message = "Congratulations! Your research submission has been approved."
    else:
        subject = "Your Research Submission Has Been Rejected - PSRA"
        status_color = "#dc3545"
        status_message = "We're sorry, but your research submission has been rejected."
    
    if hasattr(research, 'title'):
        title = research.title
        author_name = research.author.name if research.author else 'Unknown'
    else:
        title = research.get('title', 'Unknown')
        author_name = research.get('author_name', 'Unknown')
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: {{ status_color }}; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background-color: #f9f9f9; }
            .research-details { background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Research Submission Update</h1>
            </div>
            <div class="content">
                <p>Dear {{ user.name }},</p>
                
                <p>{{ status_message }}</p>
                
                <div class="research-details">
                    <p><strong>Title:</strong> {{ title }}</p>
                    <p><strong>Author:</strong> {{ author_name }}</p>
                </div>
                
                {% if reason %}
                <p><strong>Reason:</strong> {{ reason }}</p>
                {% endif %}
                
                <p>Best regards,<br>PSRA Team</p>
            </div>
            <div class="footer">
                <p>This is an automated notification from the PSRA website.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_body = render_template_string(html_template, user=user, title=title, 
                                        author_name=author_name, status_message=status_message,
                                        status_color=status_color, reason=reason)
    
    return send_email(subject, [user.email], html_body)
