import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Reservation(SqlAlchemyBase):
    __tablename__ = 'reservations'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    number_of_people = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    phonenumber = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    date_time = sqlalchemy.Column(sqlalchemy.String)
