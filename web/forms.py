from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, ValidationError

def validate_year(form, field):
    year = field.data
    for digit in year:
        if ord(digit) > 57 or ord(digit) < 48:
            raise ValidationError('Year should be 4-digit number')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[])
    password = PasswordField('Password', validators=[])
    submit = SubmitField('Sign In')


class HomeForm(FlaskForm):
    uploadFile = FileField('Upload file',validators=[])
    submit = SubmitField('Sign In')

class CreateForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min = 1, max = 10)])
    author = StringField('Author', validators=[DataRequired(), Length(min = 1, max = 10)])
    year = StringField('Year', validators=[DataRequired(), Length(min = 4, max = 4), validate_year])
    submit = SubmitField('Create')



