import sqlalchemy


from .db_session import SqlAlchemyBase


class RestaurantTypes(SqlAlchemyBase):
    __tablename__ = 'restaurant_types'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    type_name = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    only_vip = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    type_name_en = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)

