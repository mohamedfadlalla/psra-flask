from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from models import User

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
    batch_number = SelectField('Batch Number', choices=[('', 'Select batch')] + [(str(i), str(i)) for i in range(1, 59)], validators=[Optional()])
    is_member = BooleanField('Are you a member of the University of Khartoum Pharmacy?', validators=[DataRequired()])
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

    def validate_batch_number(self, batch_number):
        if self.account_type.data in ['undergraduate', 'graduate', 'alumni'] and not batch_number.data:
            raise ValidationError('Batch number is required for students and alumni.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Pharmacology', 'Pharmacology'),
        ('Clinical Pharmacy', 'Clinical Pharmacy'),
        ('Research Skills', 'Research Skills')
    ], validators=[DataRequired()])
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
    batch_number = SelectField('Batch Number', choices=[('', 'Select batch')] + [(str(i), str(i)) for i in range(1, 59)], validators=[Optional()])
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

    def validate_batch_number(self, batch_number):
        if self.account_type.data in ['undergraduate', 'graduate', 'alumni'] and not batch_number.data:
            raise ValidationError('Batch number is required for students and alumni.')

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
