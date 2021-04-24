import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Comments(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    rate = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    number_of_order = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    comment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
