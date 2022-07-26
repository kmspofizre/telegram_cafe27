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
    phone = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    working_hours = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    working_days = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    requested = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    in_favourite = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    vip_owner = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    media = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    score = sqlalchemy.Column(sqlalchemy.REAL, nullable=True)
    average_price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('restaurant_types.id'), nullable=False)
    owner = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    confirmed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    number_of_scores = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    total_score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    type_id = orm.relation('RestaurantTypes')
    owner_id = orm.relation('User')

