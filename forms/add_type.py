from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class TypeForm(FlaskForm):
    name = StringField('Название категории', validators=[DataRequired()])
    english_name = StringField('Название категории на английском', validators=[DataRequired()])
    submit = SubmitField('Добавить')