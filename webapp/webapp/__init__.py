from flask import Flask, render_template, flash, redirect, request, url_for, jsonify
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.contrib.fixers import ProxyFix

from webapp.model import * #db, Users
from webapp.forms import LoginForm
from webapp.settings.views import settings

# Словарь используемых классов
classes_dict_list = [
    {'id': 1, 'label': 'cats', 'bootstrap_class': 'badge badge-primary'},
    {'id': 2, 'label': 'dogs', 'bootstrap_class': 'badge badge-secondary'},
    {'id': 3, 'label': 'cars', 'bootstrap_class': 'badge badge-success'},
    {'id': 4, 'label': 'humans', 'bootstrap_class': 'badge badge-danger'},
    {'id': 5, 'label': 'landscapes', 'bootstrap_class': 'badge badge-warning'},
    {'id': 6, 'label': 'food', 'bootstrap_class': 'badge badge-info'},
    {'id': 7, 'label': 'cities', 'bootstrap_class': 'badge badge-light'},
    {'id': 8, 'label': 'documents', 'bootstrap_class': 'badge badge-dark'},
    {'id': 9, 'label': 'other', 'bootstrap_class': 'badge badge-secondary'}
    ]

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(settings, url_prefix='/settings')

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(user_id)


    @app.route('/')
    @login_required
    def index():
        title = 'Photo Analyzer'
        if current_user.is_authenticated:
            user = current_user.login
        else:
            user = 'guest'
        return render_template('index.html', page_title=title, user=user)


    @app.route('/login')
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        title = 'Авторизация'
        login_form = LoginForm()
        return render_template('login.html', page_title=title, form=login_form)

    @app.route('/process-login', methods=['POST'])
    def process_login():
        form = LoginForm()
        if form.validate_on_submit():
            user = Users.query.filter(Users.login == form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Вы успешно зашли на сайт')
                return redirect(url_for('index'))

        flash('Ошибка входа')
        return redirect(url_for('login'))
    
    @app.route('/logout')
    def logout():
        logout_user()
        flash('Вы успешно разлогинились')
        return redirect(url_for('index'))

    @app.route('/search')
    def search():
        class_list = []
        # Получаем список классов фильтра из GET-запроса
        for cl in classes_dict_list:
            if request.args.get(cl['label'], 'false') != 'false':
                class_list.append(cl['label'])
        
        app.logger.info(class_list)

        # Получаем даты начала и конца периода создания фотографии из GET-запроса
        start_date = request.args.get('start_date', '1970-01-01')
        end_date = request.args.get('end_date', '3000-01-01')
        
        # Заполняем пустые значения границ периода
        if start_date!='':   
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.strptime('1970-01-01', '%Y-%m-%d')
        if end_date!='':
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date = datetime.strptime('3000-01-01', '%Y-%m-%d')
        
        try:
            current_user_pref = UserPreferences.query.filter(UserPreferences.user_id==current_user.id).first()
            threshold = current_user_pref.classification_threshold
            
            # Исключаем ошибку при получении целых значений порога отнесения
            if threshold > 1:
                threshold = threshold / 100

            print(start_date, end_date, threshold)
            print(type(start_date), type(end_date), type(threshold))

            # Формируем запрос в базу
            sub = db.session.query(db.func.max(Algorithms.create_date).label('max_date')).subquery()
            selected_photos = db.session.query((Photos.id).label("id"), (Photos.name).label("name"), \
                (Classes.name).label("class_name"), (Classes.id).label("class_id"), \
                (photosclasses.c.weight).label("weight"), (Photos.path).label("folder_path")). \
                join(photosclasses, Classes, Folders, StorageUsers, Users, Algorithms). \
                filter(photosclasses.c.weight>threshold, Classes.name.in_(class_list), \
                Users.id==current_user.id, Algorithms.create_date==sub.c.max_date, \
                Photos.create_date.between(start_date, end_date)). \
                distinct(). \
                all()
            
            # Формируем html текст с результатами поиска в базе
            ph_list = []
            for ph in selected_photos:
                # ph_str = '<li class=\"list-group-item\">{0} {1} {2} {3}</li>\n' \
                # .format(str(ph.id), str(ph.name), str(ph.class_name), str(ph.weight))
                ph_str = '<li class="list-group-item col-xs-8"><a href="https://www.dropbox.com/preview{4}?personal" target="_blank">{0} {1} {2} {3}</a>\n' \
                .format(
                    str(ph.id), #0
                    str(ph.name), #1
                    str(ph.class_name), #2
                    str(ph.weight), #3
                    str(ph.folder_path) #4
                )
                ph_str += '<a  class="{0}">{1}</a>'.format(classes_dict_list[ph.class_id-1]['bootstrap_class'], classes_dict_list[ph.class_id-1]['label'])
                ph_str += '</li>'
                ph_list.append(ph_str)


            #print(ph_list)

            # Возвращаем в ajax результат поиска в базе
            return jsonify(result=ph_list)
        
        except Exception as e:
            print(e)
            return jsonify(result='error')

    return app

if __name__ == '__main__' :
    app.run(host='0.0.0.0')

