from webapp import db, create_app
from webapp.model import Storages, Classes

# Словарь классов
classes_dict = [
    {'id': 1, 'label': 'cats'},
    {'id': 2, 'label': 'dogs'},
    {'id': 3, 'label': 'cars'},
    {'id': 4, 'label': 'humans'},
    {'id': 5, 'label': 'landscapes'},
    {'id': 6, 'label': 'food'},
    {'id': 7, 'label': 'cities'},
    {'id': 8, 'label': 'documents'},
    {'id': 9, 'label': 'other'}
    ]

app = create_app()
db.create_all(app=app)

with app.app_context():
    # Создаем записи в таблице storages
    dropbox = Storages(id=1, name='dropbox', full_path='')
    yadisk = Storages(id=2, name='yadisk', full_path='')

    db.session.add(dropbox)
    db.session.add(yadisk)
    
    # Создаем словарь базовых классов
    for item in classes_dict:
        class_ = Classes(id=(classes_dict.index(item)+1), name=item['label'])
        db.session.add(class_)
    
    db.session.commit()
   
