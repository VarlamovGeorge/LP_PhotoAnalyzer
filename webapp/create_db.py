from webapp import db, create_app
from webapp.model import Storages

app = create_app()
db.create_all(app=app)

with app.app_context():
    dropbox = Storages(id=1, name='dropbox', full_path='')
    yadisk = Storages(id=2, name='yadisk', full_path='')

    db.session.add(dropbox)
    db.session.add(yadisk)

    db.session.commit()
   
