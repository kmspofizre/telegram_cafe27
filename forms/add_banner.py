from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, DateField, TimeField, FileField
from wtforms.validators import DataRequired


class BannerForm(FlaskForm):
    text = TextAreaField('Текст баннера')
    image = FileField('Фото')
    publication_date = DateField('Дата публикации', validators=[DataRequired()])
    publication_time = TimeField('Время публикации', validators=[DataRequired()])
    submit = SubmitField('Добавить')