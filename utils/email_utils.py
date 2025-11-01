from flask import current_app, render_template_string
from flask_mail import Message
from models import User
import logging

def send_email(subject, recipients, html_body, text_body=None):
    """
    Send an email using Flask-Mail with error handling.

    Args:
        subject (str): Email subject
        recipients (list): List of recipient email addresses
        html_body (str): HTML content of the email
        text_body (str, optional): Plain text version of the email

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get sender from environment or app config
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
        logging.info(f"Email sent successfully to {len(recipients)} recipients: {subject}")
        return True

    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        # Don't raise exception to avoid breaking the main application flow
        return False

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
            if send_email(subject, batch_emails, html_body, text_body):
                success_count += len(batch_emails)
            else:
                failure_count += len(batch_emails)

    logging.info(f"Event notification sent: {success_count} successful, {failure_count} failed")
    return success_count, failure_count
