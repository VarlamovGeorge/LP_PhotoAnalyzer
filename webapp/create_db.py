import os
import sys
import random
from datetime import datetime
from getpass import getpass
from webapp import db, create_app
from webapp.model import *

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

# Указываем путь папки, из которой все jpg-файлы попадут в БД
src_path = 'C:\\Users\\Jenkins\\Desktop\\ремонт'

app = create_app()
db.create_all(app=app)

def create_new():
    try:
        app = create_app()
        db.create_all(app=app)

        with app.app_context():
            # Создаем записи в таблице storages
            dropbox = Storages(id=1, name='dropbox', full_path='https://www.dropbox.com')
            yadisk = Storages(id=2, name='yadisk', full_path='https://disk.yandex.ru/')
            NAS = Storages(id=3, name='NAS', full_path='')

            db.session.add(dropbox)
            db.session.add(yadisk)
            db.session.add(NAS)
            
            # Создаем словарь базовых классов
            for item in classes_dict:
                class_ = Classes(id=(classes_dict.index(item)+1), name=item['label'])
                db.session.add(class_)
            
            # Создаем фиктивный алгоритм в справочнике используемых алгоритмов
            alg_fict = Algorithms(id=0, name='test', create_date=datetime.strptime('2000-01-01', '%Y-%m-%d'))
            db.session.add(alg_fict)

            db.session.commit()

    except:
        print('ОШИБКА при попытке создания новой БД: Возможно Вы не удалили старую базу...')
        sys.exit(0)
       
def fill_db():
    # Подключаем базу
    #app = create_app()
    #db.create_all(app=app)
    global src_path
    change_src_path=''
    while (change_src_path!='y') or (change_src_path!='n'):
        change_src_path = input('Копируемая папка: {}. Хотите изменить? (y/n)'.format(src_path))
        if change_src_path=='y':
            src_path = input('Введите полный адрес папки, которую надо скопировать в БД:')
        
        elif change_src_path=='n':
            break
    
    # Читаем файлы из папки и всех вложенных
    files_list = []
    for i in os.walk(src_path):
        files_list.append(i)
        # [(('test/cgi-bin', ['backup', 'another'], ['hello.py']), ...]

    # Список словарей path-file, с файлами jpg
    jpg_files_list = []
    # Множество путей, содержащих файлы jpg
    jpg_folders_set = set({})
    for address, dirs, files in files_list:
        for file in files:
            if file.lower().endswith(('.jpg')):
                jpg_files_list.append({'path':address, 'file': file})
                jpg_folders_set.add(address)

    print(jpg_folders_set)
    print(jpg_files_list)

    # Работа с базой
    with app.app_context():
        # Очищаем таблицы photos_classes, folders и photos
        Folders.query.delete()
        Photos.query.delete()
        db.session.commit()
        phcldel = photosclasses.delete()
        db.session.execute(phcldel)
        print('Данные в таблицах photos_classes, folders и photos очищены.')

        # Записываем множество папок, содержащих jpg-файлы
        for folder in jpg_folders_set:
            db.session.add(Folders(local_path=folder, storage_user_id=1))
        
        db.session.commit()
        print('Новые данные добавлены в таблицу folders')
        
        # Добавляем jpg-файлы в таблицу photos
        for file in jpg_files_list:
            file_folder = db.session.query(Folders).filter(Folders.local_path==file['path']).first()
            print(file['file'],file['path'], file_folder.id)
            
            db.session.add(Photos(name=file['file'], create_date=datetime.now(), status='1', folder_id=file_folder.id))

        db.session.commit()

        # Заполняем таблицу связей photos_classes для связи фотографий и классов с весами weights
        for photo in db.session.query(Photos).order_by(Photos.id): 
            ph_id = photo.id
            cl_id1 = random.randint(1, Classes.query.count())
            cl_id2 = random.randint(1, Classes.query.count())
            while cl_id2==cl_id1:
                cl_id2 = random.randint(1, Classes.query.count())

            statement = photosclasses.insert().values(photo_id=ph_id, class_id=cl_id1, weight=round(random.random(),5), alg_id=0)
            db.session.execute(statement)
            #db.session.commit()
            statement = photosclasses.insert().values(photo_id=ph_id, class_id=cl_id2, weight=round(random.random(),5), alg_id=0)
            db.session.execute(statement)
            db.session.commit()

        print('Отнесение фотографий к классам выполнено.')

def create_admin():
    # Вносим в БД дефолтного пользователя с id=0
    while True:
        pass1 = getpass('Введите пароль для пользователя admin:')
        pass2 = getpass('Повторите пароль:')

        if not pass1 == pass2:
            print('Пароли не совпадают! Пользователь admin не создан...')
            #db.session.rollback()
        else:
            break

    with app.app_context():
        new_user = Users(id=0, login='admin')
        new_user.set_password(pass1)

        db.session.add(new_user)
        db.session.commit()

        print('Администратор добавлен')


def main():
    choosen_act = input('1 - только создание новой БД; \n \
    2 - (1)+заполнение её данными из папки {};\n \
    3 - (2)+создание пользователя admin; \n \
    q - выход:\n'.format(src_path))
    if choosen_act=='1':
        create_new()
    elif choosen_act=='2':
        create_new()
        fill_db()
    elif choosen_act=='3':
        create_new()
        fill_db()
        create_admin()
    elif choosen_act=='q':
        sys.exit(0)
    else:
        main()

if __name__ == '__main__':
    main()