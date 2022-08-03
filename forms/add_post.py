from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    header = StringField('Заголовок статьи', validators=[DataRequired()])
    text = TextAreaField('Текст статьи', validators=[DataRequired()])
    media = MultipleFileField('Фото')
    submit = SubmitField('Добавить')