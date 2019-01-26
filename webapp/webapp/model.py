from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Algorithms(db.Model):
    __tablename__ = 'algorithms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    create_date = db.Column(db.DateTime, nullable=False)
    #parents = db.relationship("PhotosClasses", back_populates="child")

    def __repr__(self):
        return '<Algorithm {}>'.format(self.name)


photosclasses = db.Table('photos_classes',
    db.Column('photo_id', db.Integer, db.ForeignKey('photos.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'), primary_key=True),
    db.Column('alg_id', db.Integer, db.ForeignKey('algorithms.id'), primary_key=True),
    db.Column('weight', db.Float, nullable=False))


class Classes(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=True)
    photos = db.relationship('Photos', secondary=photosclasses, lazy='subquery', backref=db.backref('photos', lazy=True))

    def __repr__(self):
        return '<Class {}>'.format(self.name)


class Photos(db.Model):
    STATUS_NEED_RESYNC = 0
    STATUS_NEED_CLASSIFY = 1
    STATUS_OK = 100

    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String, nullable=False)
    longtitude = db.Column(db.Integer)
    latitude = db.Column(db.Integer)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=False)
    #remote_id = db.Column(db.String)
    size = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    status = db.Column(db.Integer, nullable=False)

    dropb_path = db.Column(db.String)
    dropb_file_id = db.Column(db.Integer)
    dropb_file_rev = db.Column(db.String)
    dropb_hash = db.Column(db.String)

    classes = db.relationship('Classes', secondary=photosclasses, lazy='subquery', backref=db.backref('classes', lazy=True))

    def __repr__(self):
        return '<Image {}>'.format(self.name)


class Folders(db.Model):
    __tablename__ = 'folders'
    id = db.Column(db.Integer, primary_key=True)
    local_path = db.Column(db.String, unique=True, nullable=False)
    storage_user_id = db.Column(db.Integer, db.ForeignKey('storage_users.id'), nullable=False)
    photos = db.relationship('Photos', backref='folders', lazy=True)

    def __repr__(self):
        return '<Folder {}>'.format(self.local_path)


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)
    preferences = db.relationship('UserPreferences', backref='users', lazy=True)
    storageusers = db.relationship('StorageUsers', backref='users', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.login)



