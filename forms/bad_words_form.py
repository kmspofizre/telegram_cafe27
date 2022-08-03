from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired


class BadWordsForm(FlaskForm):
    words = TextAreaField('Запрещенные слова', validators=[DataRequired()])
    lenght = IntegerField('Длительность блокировки (в минутах)', validators=[DataRequired()])
    submit = SubmitField('Сохранить')