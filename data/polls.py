import sqlalchemy


from .db_session import SqlAlchemyBase


class Poll(SqlAlchemyBase):
    __tablename__ = 'polls'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    header = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    variants = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    answers = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    datetime = sqlalchemy.Column(sqlalchemy.DATETIME, nullable=False)
    message_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
