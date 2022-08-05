from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, TimeField, BooleanField
from wtforms.validators import DataRequired


class PollForm(FlaskForm):
    name = StringField('Название опроса', validators=[DataRequired()])
    variants = TextAreaField('Варианты (разделенные знаком ";")', validators=[DataRequired()])
    publication_date = DateField('Дата публикации', validators=[DataRequired()])
    publication_time = TimeField('Время публикации', validators=[DataRequired()])
    is_anon = BooleanField('Анонимный опрос')
    submit = SubmitField('Добавить')