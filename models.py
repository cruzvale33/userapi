from enum import unique
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from config import Config


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(32), index = True, unique=True)
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String(100))
    photo = db.Column(db.Text, nullable=True)#Data to render the pic in browsers
    token = db.Column(db.Text, nullable=True)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration = 600):
        
        s = Serializer(Config.SECRET_KEY)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(Config.SECRET_KEY)
        
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user if user.token == token else None
    
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return self.id
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key = True)
    title =  db.Column(db.String(255))
    description =  db.Column(db.String(255))
    start_date =  db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    formatted_start_date = db.column_property(db.cast(start_date, db.String))
    formatted_due_date = db.column_property(db.cast(due_date, db.String))


    def get_id(self):
        try:
            return self.id
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')