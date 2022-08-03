from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired


class SpamForm(FlaskForm):
    mes = IntegerField('Количество одинаковых сообщений подряд', validators=[DataRequired()])
    lenght = IntegerField('Длительность блокировки (в минутах)', validators=[DataRequired()])
    submit = SubmitField('Сохранить')