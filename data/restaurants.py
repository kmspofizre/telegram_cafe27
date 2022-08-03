import sqlalchemy
from sqlalchemy import orm


from .db_session import SqlAlchemyBase


class Restaurant(SqlAlchemyBase):
    __tablename__ = 'restaurants'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    address = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    coordinates = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)
    phone = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    working_hours = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    requested = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)
    in_favourite = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    vip_owner = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    media = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    score = sqlalchemy.Column(sqlalchemy.REAL, nullable=False, default=0)
    average_price = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    owner = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=True)
    confirmed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    number_of_scores = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    total_score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    name_en = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    description_en = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)
    address_en = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    working_hours_en = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)

    owner_id = orm.relation('User')

