from webapp.model import db

class Storages(db.Model):
    __tablename__ = 'storages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    full_path = db.Column(db.String, nullable=False)
    api_key = db.Column(db.String)
    storageusers = db.relationship('StorageUsers', backref='storages', lazy=True)

    def __repr__(self):
        return '<Storage name {}>'.format(self.name)


class StorageUsers(db.Model):
    __tablename__ = 'storage_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    credentials = db.Column(db.Text)
    storage_id = db.Column(db.Integer, db.ForeignKey('storages.id'), nullable=False)
    global_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    folders = db.relationship('Folders', backref='storageusers', lazy=True)

    def __repr__(self):
        return '<Storage user {}>'.format(self.name)

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    classification_threshold = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<User preferences {}>'.format(self.id)
