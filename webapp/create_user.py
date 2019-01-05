from getpass import getpass
import sys

from webapp import create_app
from webapp.model import db, Users

app = create_app()

with app.app_context():
    username = input('Введите имя пользователя:')

    if Users.query.filter(Users.login == username).count():
        print('Такой пользователь уже существует')
        sys.exit(0)

    pass1 = getpass('Введите пароль:')
    pass2 = getpass('Повторите пароль:')

    if not pass1 == pass2:
        print('Пароли не совпадают!')
        sys.exit(0)

    new_user = Users(login=username)
    new_user.set_password(pass1)

    db.session.add(new_user)
    db.session.commit()
    print('Добавлен user с id={}'.format(new_user.id))