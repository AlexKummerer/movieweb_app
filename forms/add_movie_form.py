from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class AddMovieForm(FlaskForm):
    name = StringField("Movie Name", validators=[DataRequired()])
    director = StringField("Director", validators=[DataRequired()])
    year = IntegerField("Year", validators=[DataRequired()])
    rating = FloatField(
        "Rating", validators=[DataRequired(), NumberRange(min=0, max=10)]
    )
    submit = SubmitField("Add Movie")
