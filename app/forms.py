from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, SelectField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[
        ('organizer', 'Organizer'), 
        ('presenter', 'Presenter'), 
        ('listener', 'Listener')], 
        validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    title = StringField('Presentation Title', validators=[DataRequired()])
    file = FileField('Upload File', validators=[DataRequired()])
    submit = SubmitField('Upload')

class FeedbackForm(FlaskForm):
    feedback_type = SelectField('Feedback Type', choices=[
        ('presenter', 'About Presenter'), 
        ('question', 'About Question'), 
        ('environment', 'About Environment')])
    comment = TextAreaField('Your Feedback')
    submit = SubmitField('Submit Feedback')