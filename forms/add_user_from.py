from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddUserForm(FlaskForm):
    name = StringField("User Name", validators=[DataRequired()])
    submit = SubmitField("Add User")
