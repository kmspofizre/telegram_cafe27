import sqlalchemy


from .db_session import SqlAlchemyBase


class Poll(SqlAlchemyBase):
    __tablename__ = 'polls'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
