from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class PhraseForm(FlaskForm):
    name = StringField('Текст фразы', validators=[DataRequired()])
    submit = SubmitField('Добавить')