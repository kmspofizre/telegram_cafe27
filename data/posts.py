import sqlalchemy
from sqlalchemy import orm


from .db_session import SqlAlchemyBase


class Posts(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    header = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)
    media = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    date_of_publication = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)

    author_id = orm.relation('User')