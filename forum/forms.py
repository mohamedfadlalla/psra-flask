from flask_wtf import FlaskForm
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
    batch_number = SelectField('Batch Number', choices=[(str(i), str(i)) for i in range(1, 59)], validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    whatsapp_number = StringField('WhatsApp Number (Optional)', validators=[Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    agree_terms = BooleanField('I agree to the Terms and Conditions', validators=[DataRequired()])
    submit = SubmitField('Create Account')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
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
    batch_number = SelectField('Batch Number', choices=[(str(i), str(i)) for i in range(1, 59)], validators=[DataRequired()])
    email = StringField('Email', render_kw={'readonly': True})
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    whatsapp_number = StringField('WhatsApp Number (Optional)', validators=[Length(max=20)])
    submit = SubmitField('Update Profile')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')
