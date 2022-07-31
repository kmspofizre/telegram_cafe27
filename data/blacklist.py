import sqlalchemy

from .db_session import SqlAlchemyBase


class Blacklist(SqlAlchemyBase):
    __tablename__ = 'blacklist'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    telegram_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    reason = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    username = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)