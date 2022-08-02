import sqlalchemy


from .db_session import SqlAlchemyBase


class Posts(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    header = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)
    media = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
