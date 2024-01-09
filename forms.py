from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email, ValidationError
from flask_ckeditor import CKEditorField
import re
# IMPT : To use bootstrap5 - do not install flask-bootstrap - install Bootstrap-Flask

# Below is an example of custom validation for password
def validate_password_strength(form, field):
    password = field.data
    if not password:
        raise ValidationError("Password is required")

    if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
        raise ValidationError(
            "Password must contain at least 8 characters, including one letter, one number, and one special character")

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(message="Invalid email address")])
    password = PasswordField("Password", validators=[DataRequired(), validate_password_strength])
    name = StringField("Name",validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(message="Invalid email address")])
    password = PasswordField("Password", validators=[DataRequired(), validate_password_strength])
    submit = SubmitField("Let Me In!")

class CommentForm(FlaskForm):
    comment_text = CKEditorField('Comment',validators=[DataRequired()])
    submit = SubmitField('Submit Comment')
