from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import SubmitField


class FilterForm(FlaskForm):
    period = SelectField("Период")
    category = SelectField("Категория")
    submit = SubmitField("Применить")
