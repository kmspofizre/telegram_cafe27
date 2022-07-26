import sqlalchemy
from sqlalchemy import orm


from .db_session import SqlAlchemyBase


class Scores(SqlAlchemyBase):
    __tablename__ = 'scores'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    restaurant = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('restaurants.id'), nullable=False)
    score = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    user_id = orm.relation('User')
    restaurant_id = orm.relation('Restaurant')