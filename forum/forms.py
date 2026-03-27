from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from models import User

# University choices - hardcoded list
UNIVERSITY_CHOICES = [
    ('', 'Select your university (optional)'),
    ('1', 'University of Khartoum'),
    ('2', 'Sudan University of Science and Technology'),
    ('3', 'University of Gezira'),
    ('4', 'Neelain University'),
    ('5', 'International University of Africa'),
    ('6', 'Al Zaiem Al Azhari University'),
    ('7', 'National University-Sudan'),
    ('8', 'Omdurman Islamic University'),
    ('9', 'University of Medical Sciences and Technology'),
    ('10', 'National Ribat University'),
    ('11', 'Karary University'),
    ('12', 'Ahfad University for Women'),
    ('13', 'University of Shendi'),
    ('14', 'Merowe University of Technology'),
    ('15', 'Elsheikh Abdallah Elbadri University'),
    ('16', 'University of Kassala'),
    ('17', 'University of Gadarif'),
    ('18', 'Red Sea University'),
    ('19', 'University of Kordofan'),
    ('20', 'University of Nyala'),
    ('21', 'University of Bahri'),
    ('22', 'The Future University'),
    ('23', 'Nile Valley University'),
    ('24', 'Omdurman Ahlia University'),
    ('25', 'University of Bakhtalruda'),
]

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    account_type = SelectField('Account Type', choices=[
        ('undergraduate', 'Undergraduate Student'),
        ('graduate', 'Graduate (Alumni)'),
        ('alumni', 'Alumni'),
        ('researcher', 'Researcher')
    ], validators=[DataRequired()])
    university_id = SelectField('University', choices=UNIVERSITY_CHOICES, validators=[Optional()])
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    whatsapp_number = StringField('WhatsApp Number (Optional)', validators=[Length(max=20)])
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    agree_terms = BooleanField('I agree to the Terms and Conditions', validators=[DataRequired()])
    submit = SubmitField('Create Account')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.strip()).first()
        if user:
            raise ValidationError('Email already registered.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Comment')

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    account_type = SelectField('Account Type', choices=[
        ('undergraduate', 'Undergraduate Student'),
        ('graduate', 'Graduate (Alumni)'),
        ('alumni', 'Alumni'),
        ('researcher', 'Researcher')
    ], validators=[DataRequired()])
    headline = StringField('Headline', validators=[Length(max=200)])
    location = StringField('Location', validators=[Length(max=100)])
    about = TextAreaField('About', validators=[Length(max=1000)])
    university_id = SelectField('University', choices=UNIVERSITY_CHOICES, validators=[Optional()])
    email = StringField('Email', render_kw={'readonly': True})
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    whatsapp_number = StringField('WhatsApp Number (Optional)', validators=[Length(max=20)])
    skills = StringField('Skills (comma-separated)', validators=[Length(max=500)])
    # These fields will be handled dynamically via JavaScript
    # The actual data will be submitted as JSON strings
    education_data = StringField('Education Data', validators=[Length(max=5000)])
    experience_data = StringField('Experience Data', validators=[Length(max=5000)])
    linkedin_url = StringField('LinkedIn URL', validators=[Length(max=200)])
    website_url = StringField('Website URL', validators=[Length(max=200)])
    languages = StringField('Languages (comma-separated)', validators=[Length(max=500)])
    certifications = TextAreaField('Certifications', validators=[Length(max=1000)])
    projects = TextAreaField('Projects/Portfolio', validators=[Length(max=1000)])
    publications = TextAreaField('Publications/Research', validators=[Length(max=1000)])
    professional_summary = TextAreaField('Professional Summary', validators=[Length(max=1000)])
    open_to_mentor = BooleanField('Open to Mentorship Requests')
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    submit = SubmitField('Update Profile')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Send Message')


class ResearchSubmissionForm(FlaskForm):
    """Form for submitting a new research."""
    title = StringField('Research Title', validators=[
        DataRequired(message='Title is required.'),
        Length(min=5, max=500, message='Title must be between 5 and 500 characters.')
    ])
    researcher_name = StringField('Researcher Name', validators=[
        DataRequired(message='Researcher name is required.'),
        Length(min=2, max=200, message='Name must be between 2 and 200 characters.')
    ])
    department = SelectField('Department', validators=[
        DataRequired(message='Department is required.')
    ], choices=[
        ('Pharmaceutics & Drug Delivery', 'Pharmaceutics & Drug Delivery'),
        ('Pharmacology & Toxicology', 'Pharmacology & Toxicology'),
        ('Clinical Pharmacy & Pharmacy Practice', 'Clinical Pharmacy & Pharmacy Practice'),
        ('Pharmaceutical Chemistry', 'Pharmaceutical Chemistry')
    ])
    year = IntegerField('Year of Publication', validators=[
        DataRequired(message='Year is required.'),
        NumberRange(min=1990, max=2030, message='Year must be between 1990 and 2030.')
    ])
    doi_url = StringField('DOI Link', validators=[
        Optional(),
        Length(max=500, message='DOI URL must be less than 500 characters.')
    ])
    researcher_type = SelectField('Researcher Type', validators=[
        DataRequired(message='Researcher type is required.')
    ], choices=[
        ('doctor', 'Doctor'),
        ('student', 'Student')
    ])
    submit = SubmitField('Submit Research')
