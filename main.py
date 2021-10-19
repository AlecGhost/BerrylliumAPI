from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime as dt
import base64
import bcrypt
import hashlib

Base = declarative_base()
app = Flask(__name__)


class User(Base):
    __tablename__ = "user"
    username = Column(String(250), primary_key=True)
    api_hash = Column(String)


class Message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True)
    sender = Column(String(250), nullable=False)
    subject = Column(String)
    message = Column(JSON)
    timestamp = Column(DateTime)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class ArchivedMessage(Base):
    __tablename__ = "archived-message"
    id = Column(Integer, primary_key=True)
    sender = Column(String(250), nullable=False)
    subject = Column(String)
    message = Column(JSON)
    sent_timestamp = Column(DateTime)
    archived_timestamp = Column(DateTime)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# Establish database connection
engine = create_engine('sqlite:///messages.db')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

session = Session()


# source: https://github.com/TheMorpheus407/Python-Lets-Code/blob/master/SavePasswords.py
def check_password(password: str, hash: str):
    password = password.encode('utf-8')
    password = base64.b64encode(hashlib.sha256(password).digest())
    hash = hash.encode('utf-8')
    if bcrypt.checkpw(password, hash):
        return True
    else:
        return False


def login_required(function):
    def wrapper(**kwargs):
        username = request.args.get('username')
        api_key = request.args.get('api-key')
        user = session.query(User).get(username)
        if user and check_password(api_key, user.api_hash):
            return function(**kwargs)
        else:
            return jsonify(error={
                "Unauthorized": "Sorry, you need to identify yourself with an api key."
            }), 401

    return wrapper


@app.route('/')
def home():
    return render_template('index.html')


# HTTP GET
@app.route('/messages', endpoint='get_messages')
@login_required
def get_messages():
    messages = session.query(Message).all()
    if messages:
        return jsonify(messages=[message.to_dict() for message in messages]), 200
    else:
        return jsonify(error={"Not Found": "Sorry, there are no messages here."}), 404


@app.route('/messages/<int:id>', endpoint='get_message')
@login_required
def get_message(id):
    message = session.query(Message).filter_by(id=id).first()
    if message:
        return jsonify(message.to_dict()), 200
    else:
        return jsonify(error={"Not Found": "Sorry, there are no messages here."}), 404


@app.route('/messages/latest', endpoint='get_latest_message')
@login_required
def get_latest_message():
    message = session.query(Message).all()[-1]
    if message:
        return jsonify(message.to_dict()), 200
    else:
        return jsonify(error={"Not Found": "Sorry, there are no messages here."}), 404


@app.route('/messages/today', endpoint='get_todays_messages')
@login_required
def get_todays_messages():
    messages = [message for message in session.query(Message).all()
                if message.timestamp.date() == dt.datetime.today().date()]
    if messages:
        return jsonify(messages=[message.to_dict() for message in messages]), 200
    else:
        return jsonify(error={"Not Found": "Sorry, there are no messages here."}), 404


@app.route('/archived-messages', endpoint='get_archived_messages')
@login_required
def get_archived_messages():
    messages = session.query(ArchivedMessage).all()
    if messages:
        return jsonify(messages=[message.to_dict() for message in messages]), 200
    else:
        return jsonify(error={"Not Found": "Sorry, there are no messages here."}), 404


# HTTP POST
@app.route('/add', methods=["POST"], endpoint='add_message')
@login_required
def add_message():
    new_message = Message(
        sender=request.args.get('username'),
        subject=request.args.get('subject'),
        message=request.get_json(),
        timestamp=dt.datetime.now()
    )
    session.add(new_message)
    session.commit()
    return jsonify(response={"OK": "Successfully posted a new message."})


# HTTP DELETE
@app.route('/messages/<int:id>/delete', methods=["DELETE"], endpoint='delete_message')
@login_required
def delete_message(id):
    message = session.query(Message).get(id)
    if message:
        new_archived_message = ArchivedMessage(
            sender=message.sender,
            subject=message.subject,
            message=message.message,
            sent_timestamp=message.timestamp,
            archived_timestamp=dt.datetime.now()
        )
        session.add(new_archived_message)
        session.delete(message)
        session.commit()
        return jsonify(response={"OK": "Successfully deleted the message from the database."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a message with that id was not found in the database."}), 404


# Run app
if __name__ == '__main__':
    app.run(host='0.0.0.0')
