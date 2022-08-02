import sqlalchemy
from sqlalchemy import orm


from .db_session import SqlAlchemyBase


class Payment(SqlAlchemyBase):
    __tablename__ = 'payments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    payment_name = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    transaction_amount = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    phone = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    payment_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    user_id = orm.relation('User')