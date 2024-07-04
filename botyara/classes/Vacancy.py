from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from classes.Base import Base
from classes.User import User


class Vacancy(Base):
    __tablename__ = 'vacancies'

    id = Column(Integer, primary_key=True)
    user_tg_id = Column(Integer, ForeignKey('users.tg_id'))
    title = Column(String)
    experience = Column(String)
    salary = Column(String)
    city = Column(String)
    subway = Column(String)
    company = Column(String)
    link = Column(String)
    user = relationship('User', back_populates = 'vacancies')
