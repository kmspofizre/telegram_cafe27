from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired


class EditPostForm(FlaskForm):
    header = StringField('Заголовок статьи', validators=[DataRequired()])
    text = TextAreaField('Текст статьи', validators=[DataRequired()])
    current_media = StringField('Нынешние файлы (Перечислены в том же порядке, в котором отображены\n'
                                'уберите ненужные и оставьте разделение ;)')
    media = MultipleFileField('Фото')
    submit = SubmitField('Подтвердить')