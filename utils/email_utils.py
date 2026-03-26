from flask import current_app, render_template_string, url_for
from flask_mail import Message
from models import User, ApplicationStatus
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


def send_mentorship_request_email(alumni, student, message):
    """
    Send a mentorship request notification email to the alumni.
    
    Args:
        alumni: User model instance (the alumni/mentor receiving the request)
        student: User model instance (the student making the request)
        message: The message from the student
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    subject = f"New Mentorship Request from {student.name} - PSRA"
    
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
            .request-details { background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
            .message-box { background-color: #f0f0f0; padding: 10px; border-left: 4px solid #2D577B; margin: 10px 0; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            .btn { display: inline-block; padding: 10px 20px; background-color: #2D577B; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>New Mentorship Request</h1>
            </div>
            <div class="content">
                <p>Dear {{ alumni.name }},</p>
                
                <p>You have received a new mentorship request!</p>
                
                <div class="request-details">
                    <p><strong>From:</strong> {{ student.name }}</p>
                    <p><strong>Email:</strong> {{ student.email }}</p>
                </div>
                
                <p><strong>Message:</strong></p>
                <div class="message-box">
                    {{ message }}
                </div>
                
                <p>Log in to your PSRA dashboard to review and respond to this request.</p>
                
                <p><a href="{{ url }}" class="btn">Manage Mentorships</a></p>
                
                <p>Best regards,<br>PSRA Team</p>
            </div>
            <div class="footer">
                <p>This is an automated notification from the Pharmaceutical Studies and Research Association.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    from flask import url_for
    from flask import current_app
    
    with current_app.app_context():
        manage_url = url_for('hub.manage_mentorships', _external=True)
        html_body = render_template_string(html_template, 
                                         alumni=alumni, 
                                         student=student, 
                                         message=message,
                                         url=manage_url)
    
    return send_email(subject, [alumni.email], html_body)


def send_mentorship_response_email(student, alumni, status, message=None):
    """
    Send a mentorship response (accept/reject) notification email to the student.
    
    Args:
        student: User model instance (the student receiving the response)
        alumni: User model instance (the alumni/mentor who responded)
        status: 'accepted' or 'rejected'
        message: Optional message from the alumni
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    if status == 'accepted':
        subject = f"Your Mentorship Request Has Been Accepted - PSRA"
        status_color = "#28a745"
        status_message = "Great news! Your mentorship request has been accepted."
    else:
        subject = f"Your Mentorship Request Has Been Declined - PSRA"
        status_color = "#dc3545"
        status_message = "Unfortunately, your mentorship request has been declined."
    
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
            .response-details { background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
            .message-box { background-color: #f0f0f0; padding: 10px; border-left: 4px solid {{ status_color }}; margin: 10px 0; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Mentorship Request Update</h1>
            </div>
            <div class="content">
                <p>Dear {{ student.name }},</p>
                
                <p>{{ status_message }}</p>
                
                <div class="response-details">
                    <p><strong>Mentor:</strong> {{ alumni.name }}</p>
                    {% if alumni.alumni_profile and alumni.alumni_profile.job_title %}
                    <p><strong>Job Title:</strong> {{ alumni.alumni_profile.job_title }}</p>
                    {% endif %}
                    {% if alumni.alumni_profile and alumni.alumni_profile.company %}
                    <p><strong>Company:</strong> {{ alumni.alumni_profile.company }}</p>
                    {% endif %}
                </div>
                
                {% if message %}
                <p><strong>Message from mentor:</strong></p>
                <div class="message-box">
                    {{ message }}
                </div>
                {% endif %}
                
                {% if status == 'accepted' %}
                <p>You can now connect with your mentor through the PSRA messaging system.</p>
                {% endif %}
                
                <p>Log in to your PSRA dashboard to view more details.</p>
                
                <p>Best regards,<br>PSRA Team</p>
            </div>
            <div class="footer">
                <p>This is an automated notification from the Pharmaceutical Studies and Research Association.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_body = render_template_string(html_template, 
                                     student=student, 
                                     alumni=alumni, 
                                     status=status,
                                     status_color=status_color,
                                     status_message=status_message,
                                     message=message)
    
    return send_email(subject, [student.email], html_body)


def send_project_application_email(researcher, student, project, motivation_letter):
    """
    Send a research project application notification email to the researcher.
    
    Args:
        researcher: User model instance (the researcher receiving the application)
        student: User model instance (the student applying)
        project: ResearchProject model instance
        motivation_letter: The student's motivation letter
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    subject = f"New Application for Your Research Project: {project.title} - PSRA"
    
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
            .project-details { background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
            .student-details { background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
            .motivation-box { background-color: #f0f0f0; padding: 10px; border-left: 4px solid #2D577B; margin: 10px 0; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            .btn { display: inline-block; padding: 10px 20px; background-color: #2D577B; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>New Research Project Application</h1>
            </div>
            <div class="content">
                <p>Dear {{ researcher.name }},</p>
                
                <p>You have received a new application for your research project!</p>
                
                <div class="project-details">
                    <p><strong>Project Title:</strong> {{ project.title }}</p>
                    <p><strong>Positions Filled:</strong> {{ project_filled }} / {{ project_total }}</p>
                </div>
                
                <div class="student-details">
                    <p><strong>Applicant:</strong> {{ student.name }}</p>
                    <p><strong>Email:</strong> {{ student.email }}</p>
                </div>
                
                <p><strong>Motivation Letter:</strong></p>
                <div class="motivation-box">
                    {{ motivation_letter }}
                </div>
                
                <p>Log in to your PSRA dashboard to review and manage this application.</p>
                
                <p><a href="{{ url }}" class="btn">Manage Applications</a></p>
                
                <p>Best regards,<br>PSRA Team</p>
            </div>
            <div class="footer">
                <p>This is an automated notification from the Pharmaceutical Studies and Research Association.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    project_filled = len([a for a in project.applications if a.status == ApplicationStatus.ACCEPTED]) if project.applications else 0
    project_total = project.required_positions
    
    with current_app.app_context():
        manage_url = url_for('hub.manage_projects', _external=True)
        html_body = render_template_string(html_template, 
                                         researcher=researcher, 
                                         student=student, 
                                         project=project,
                                         motivation_letter=motivation_letter,
                                         project_filled=project_filled,
                                         project_total=project_total,
                                         url=manage_url)
    
    result = send_email(subject, [researcher.email], html_body)
    current_app.logger.info(f"Project application notification sent to {researcher.email} for project '{project.title}'")
    return result


def send_project_application_response_email(student, researcher, project, status, message=None):
    """
    Send a research project application response (accept/reject) notification email to the student.
    
    Args:
        student: User model instance (the student receiving the response)
        researcher: User model instance (the researcher who responded)
        project: ResearchProject model instance
        status: 'accepted' or 'rejected'
        message: Optional message from the researcher
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    if status == 'accepted' or status == ApplicationStatus.ACCEPTED:
        subject = f"Your Application Has Been Accepted - {project.title} - PSRA"
        status_color = "#28a745"
        status_message = "Great news! Your application for the research project has been accepted."
    elif status == 'rejected' or status == ApplicationStatus.REJECTED:
        subject = f"Your Application Has Been Declined - {project.title} - PSRA"
        status_color = "#dc3545"
        status_message = "Unfortunately, your application for the research project has been declined."
    else:
        current_app.logger.warning(f"Invalid status '{status}' passed to send_project_application_response_email. Expected 'accepted' or 'rejected'. Treating as rejected.")
        subject = f"Your Application Status Update - {project.title} - PSRA"
        status_color = "#6c757d"
        status_message = "Your application status has been updated."
    
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
            .project-details { background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
            .message-box { background-color: #f0f0f0; padding: 10px; border-left: 4px solid {{ status_color }}; margin: 10px 0; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            .btn { display: inline-block; padding: 10px 20px; background-color: #2D577B; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Research Project Application Update</h1>
            </div>
            <div class="content">
                <p>Dear {{ student.name }},</p>
                
                <p>{{ status_message }}</p>
                
                <div class="project-details">
                    <p><strong>Project Title:</strong> {{ project.title }}</p>
                    <p><strong>Researcher:</strong> {{ researcher.name }}</p>
                    <p><strong>Researcher Email:</strong> {{ researcher.email }}</p>
                </div>
                
                {% if message %}
                <p><strong>Message from researcher:</strong></p>
                <div class="message-box">
                    {{ message }}
                </div>
                {% endif %}
                
                {% if status == 'accepted' %}
                <p>You can now message the researcher through the PSRA messaging system.</p>
                <p><a href="{{ message_url }}" class="btn">Message Researcher</a></p>
                {% endif %}
                
                <p>Log in to your PSRA dashboard to view more details.</p>
                
                <p>Best regards,<br>PSRA Team</p>
            </div>
            <div class="footer">
                <p>This is an automated notification from the Pharmaceutical Studies and Research Association.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    with current_app.app_context():
        message_url = url_for('forum.conversation', user_id=researcher.id, _external=True)
        html_body = render_template_string(html_template,
                                         student=student,
                                         researcher=researcher,
                                         project=project,
                                         status=status,
                                         status_color=status_color,
                                         status_message=status_message,
                                         message=message,
                                         message_url=message_url)
    
    current_app.logger.info(f"Project application response ({status}) email sent to {student.email} for project '{project.title}'")
    return send_email(subject, [student.email], html_body)
