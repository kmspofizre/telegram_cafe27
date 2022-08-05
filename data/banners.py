import sqlalchemy


from .db_session import SqlAlchemyBase


class Banner(SqlAlchemyBase):
    __tablename__ = 'banners'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    datetime = sqlalchemy.Column(sqlalchemy.DATETIME, nullable=False)
