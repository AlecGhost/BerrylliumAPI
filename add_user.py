import base64
import bcrypt
import hashlib
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    username = Column(String(250), primary_key=True)
    api_hash = Column(String)


# Connect to Database
engine = create_engine('sqlite:///messages.db')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

session = Session()


# source: https://github.com/TheMorpheus407/Python-Lets-Code/blob/master/SavePasswords.py
def gen_password_hash(password: str):
    password = password.encode("utf-8")
    password = base64.b64encode(hashlib.sha256(password).digest())
    hashed = bcrypt.hashpw(
        password,
        bcrypt.gensalt(12)
    )
    return hashed.decode()


new_user = User(
    username=input("Username: "),
    api_hash=gen_password_hash(input("Api Key: "))
)
session.add(new_user)
session.commit()
