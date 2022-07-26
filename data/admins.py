import sqlalchemy


from .db_session import SqlAlchemyBase


class Admins(SqlAlchemyBase):
    __tablename__ = 'admins'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    username = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)