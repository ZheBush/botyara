import sqlalchemy as db

from sqlalchemy.orm import relationship
from classes.Base import Base


class User(Base):
    __tablename__ = 'users'

    tg_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    vacancies = relationship('Vacancy', back_populates = 'user')