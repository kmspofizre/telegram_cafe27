from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField,\
    SelectMultipleField, MultipleFileField, BooleanField, FileField
from wtforms.validators import DataRequired
from data import db_session
from data.restaurant_types import RestaurantTypes


db_session.global_init("db/cafe27.db")
db_sess = db_session.create_session()


class EditRestaurantForm(FlaskForm):
    name = StringField('Название заведения', validators=[DataRequired()])
    description = TextAreaField('Описание заведения', validators=[DataRequired()])
    address = StringField('Адрес заведения', validators=[DataRequired()])
    average = SelectField('Средний чек', choices=['₽', '₽₽', '₽₽₽'], validators=[DataRequired()])
    types = SelectMultipleField('Категории', choices=list(map(lambda x: x.type_name,
                                                              db_sess.query(RestaurantTypes).filter(
                                                                  RestaurantTypes.default == 0))),
                                validators=[DataRequired()])
    operating = StringField('Режим работы', validators=[DataRequired()])
    current_media = StringField('Нынешние фотографии')
    media = MultipleFileField('Фото')
    new_main_pic = FileField('Новое главное фото')
    name_en = StringField('Название заведения (англ)', validators=[DataRequired()])
    description_en = TextAreaField('Описание заведения (англ)', validators=[DataRequired()])
    address_en = StringField('Адрес заведения (англ)', validators=[DataRequired()])
    operating_en = StringField('Режим работы (англ)', validators=[DataRequired()])
    change_geopos = BooleanField('Изменить геопозицию? (Делать только если поменялся адрес)')
    submit = SubmitField('Подтвердить')
