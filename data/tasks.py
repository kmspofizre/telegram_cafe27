import sqlalchemy


from .db_session import SqlAlchemyBase


class Task(SqlAlchemyBase):
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    task_type = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    item_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    datetime = sqlalchemy.Column(sqlalchemy.DATETIME, nullable=False)
    in_work = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)

