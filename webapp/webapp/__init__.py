from flask import Flask, render_template, flash, redirect, request, url_for, jsonify
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from flask_migrate import Migrate
from datetime import datetime

from webapp.model import * #db, Users
from webapp.forms import LoginForm
from webapp.settings.views import settings

def create_app():
    app = Flask(__name__)
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
        cats = request.args.get('cats', 'false')
        if cats != 'false':
            class_list.append('cats')
        dogs = request.args.get('dogs', 'false')
        if dogs != 'false':
            class_list.append('dogs')
        humans = request.args.get('humans', 'false')
        if humans != 'false':
            class_list.append('humans')
        cars = request.args.get('cars', 'false')
        if cars != 'false':
            class_list.append('cars')
        cities = request.args.get('cities', 'false')
        if cities != 'false':
            class_list.append('cities')
        landscapes = request.args.get('landscapes', 'false')
        if landscapes != 'false':
            class_list.append('landscapes')
        food = request.args.get('food', 'false')
        if food != 'false':
            class_list.append('food')
        documents = request.args.get('documents', 'false')
        if documents != 'false':
            class_list.append('documents')
        other = request.args.get('other', 'false')
        if other != 'false':
            class_list.append('other')
        
        app.logger.info(class_list)

        start_date = request.args.get('start_date', '1970-01-01')
        end_date = request.args.get('end_date', '3000-01-01')
        
        if start_date!='':   
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date!='':
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        try:
            current_user_pref = UserPreferences.query.filter(UserPreferences.user_id==current_user.id).first()
            threshold = current_user_pref.classification_threshold
            if threshold > 1:
                threshold = threshold / 100

            print(start_date, end_date, threshold)
            print(type(start_date), type(end_date), type(threshold))

            # selected_photos = Photos.query. \
            #     join(photosclasses). \
            #     filter(photosclasses.c.weight>threshold). \
            #     join(Classes). \
            #     filter(Classes.name.in_(class_list)).distinct().all()

            selected_photos = db.session.query((Photos.id).label("id"), (Photos.name).label("name"), \
                (Classes.name).label("class_name"), (photosclasses.c.weight).label("weight")). \
                join(photosclasses, Classes). \
                filter(photosclasses.c.weight>threshold, Classes.name.in_(class_list)). \
                distinct(). \
                all()
               
            ph_list = []
            for ph in selected_photos:
                ph_str = '<li class=\"list-group-item\">'+str(ph.id)+' '+str(ph.name)+' '+str(ph.class_name)+' '+str(ph.weight)+'</li>\n'
                ph_list.append(ph_str)

            #print(ph_list)

            return jsonify(result=ph_list)
        
        except Exception as e:
            print(e)
            return jsonify(result='error')

    return app

if __name__ == '__main__' :
    app.run(host='0.0.0.0')

