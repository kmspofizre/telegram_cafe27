from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField, MultipleFileField
from wtforms.validators import DataRequired
from data import db_session
from data.restaurant_types import RestaurantTypes


db_session.global_init("db/cafe27.db")
db_sess = db_session.create_session()


class AddRestaurantForm(FlaskForm):
    name = StringField('Название заведения', validators=[DataRequired()])
    description = TextAreaField('Описание заведения', validators=[DataRequired()])
    address = StringField('Адрес заведения', validators=[DataRequired()])
    average = SelectField('Средний чек', choices=['₽', '₽₽', '₽₽₽'], validators=[DataRequired()])
    types = SelectMultipleField('Категории', choices=list(map(lambda x: x.type_name,
                                                              db_sess.query(RestaurantTypes).filter(
                                                                  RestaurantTypes.default == 0))),
                                validators=[DataRequired()])
    operating = StringField('Режим работы', validators=[DataRequired()])
    media = MultipleFileField('Фото', validators=[DataRequired()])
    submit = SubmitField('Добавить')
