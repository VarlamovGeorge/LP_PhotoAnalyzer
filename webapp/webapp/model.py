from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class PhotosClasses(Base):
    __tablename__ = 'photos_classes'
    photo_id = db.Column(db.Integer, ForeignKey('photos.id'), primary_key=True)
    class_id = db.Column(db.Integer, ForeignKey('classes.id'), primary_key=True)
    alg_id = db.Column(db.Integer, ForeignKey('algorithms.id'), primary_key=True)
    child = relationship("Child", back_populates="parents")
    parent = relationship("Parent", back_populates="children")

    def __repr__(self):
        return '<Photo {} class {} algorithm {}>'.format(self.photo_id, self.class_id, self.alg_id)

class Algorithms(db.Model):
    __tablename__ = 'algorithms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    var = db.Column(db.String, nullable=False)
    parents = relationship("PhotosClasses", back_populates="child")

    def __repr__(self):
        return '<Algorithm {}>'.format(self.name)

class Classes(db.Model):
    __tablename__ = 'classes'
    children = relationship("PhotosClasses", back_populates="parent")
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=True)

    def __repr__(self):
        return '<Class {}>'.format(self.name)

class Photos(db.Model):
    __tablename__ = 'photos'
    parents = relationship("PhotosClasses", back_populates="child")
    parent = relationship("Parent", back_populates="children")
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String, nullable=False)
    longtitude = db.Column(db.Integer)
    latitude = db.Column(db.Integer)
    folder_id = db.Column(db.Integer, ForeignKey('folders.id'), nullable=False)

    def __repr__(self):
        return '<Image {}>'.format(self.name)

class Folders(db.Model):
    __tablename__ = 'folders'
    children = relationship("Child", back_populates="parent")
    parent = relationship("Parent", back_populates="children")
    id = db.Column(db.Integer, primary_key=True)
    local_path = db.Column(db.String, unique=True, nullable=False)
    storage_id = db.Column(db.Integer, ForeignKey('storages.id'), nullable=False)

    def __repr__(self):
        return '<Folder {}>'.format(self.local_path)

class Storages(db.Model):
    __tablename__ = 'storages'
    children = relationship("Child", back_populates="parent")
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    full_path = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Storage name {}>'.format(self.name)

class StorageUsers(db.Model):
    __tablename__ = 'storage_users'
    parent = relationship("Parent", back_populates="children")
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)
    storage_id = db.Column(db.Integer, ForeignKey('storages.id'), nullable=False)
    global_user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return '<Storage user {}>'.format(self.login)

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    children = relationship("Child", back_populates="parent")
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.login)