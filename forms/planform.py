from flask_wtf import FlaskForm
from wtforms import DateField, TimeField, SubmitField
from wtforms.validators import DataRequired


class PlannerForm(FlaskForm):
    date = DateField('Дата публикации', validators=[DataRequired()])
    time = TimeField('Время публикации', validators=[DataRequired()])
    submit = SubmitField('Send')