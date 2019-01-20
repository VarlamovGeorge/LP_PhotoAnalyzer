from flask import Flask, render_template, flash, redirect, request, url_for
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from flask_migrate import Migrate

from webapp.model import db, Users
from webapp.settings.models import StorageUsers, Storages, UserPreferences
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

    @app.route('/search', methods=['POST'])
    def search():
        selected_classes = request.form.getlist('class')
        selected_start_date = request.form.get('start_date')
        selected_end_date = request.form.get('end_date')
        print(selected_classes, selected_start_date, selected_end_date)
        return redirect(url_for('index'))

    return app

if __name__ == '__main__' :
    app.run(host='0.0.0.0')

