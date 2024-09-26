# tcc_good_code/app/domain/entities/user.py

from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    age = Column(Integer, nullable=False)
    address = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    services = Column(String, nullable=False)
    expiration_date = Column(Date, nullable=False)
    notes = Column(String, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
