from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional

class MentorshipRequestForm(FlaskForm):
    message = TextAreaField('Message to Mentor', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Send Request')


class ResearchProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Project Description', validators=[DataRequired(), Length(max=5000)])
    required_positions = IntegerField('Required Positions', default=1, validators=[DataRequired()])
    skills = StringField('Required Skills (comma-separated)', validators=[Length(max=500)])
    submit = SubmitField('Create Project')

class ApplicationForm(FlaskForm):
    motivation_letter = TextAreaField('Motivation Letter', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Submit Application')

