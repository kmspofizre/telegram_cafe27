from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired


class VIPForm(FlaskForm):
    price = IntegerField('Цена VIP статуса', validators=[DataRequired()])
    submit = SubmitField('Сохранить')