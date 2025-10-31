from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
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
    headline = StringField('Headline', validators=[Length(max=200)])
    location = StringField('Location', validators=[Length(max=100)])
    about = TextAreaField('About', validators=[Length(max=1000)])
    batch_number = SelectField('Batch Number', choices=[(str(i), str(i)) for i in range(1, 59)], validators=[DataRequired()])
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
    cover_photo = FileField('Cover Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
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
