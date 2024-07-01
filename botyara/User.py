import sqlalchemy as db

from Base import Base


class User(Base):
    __tablename__ = 'users_test'

    tg_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
