import sqlalchemy


from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    telegram_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, nullable=False)
    username = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    date_of_appearance = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    favourite = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False, default=0)
    owner = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    is_vip = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    name = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    user_link = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    moderator = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=0)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)