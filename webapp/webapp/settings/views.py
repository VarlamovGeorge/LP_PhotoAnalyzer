from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from flask import current_app as app
from flask_login import current_user, login_required

from dropbox import DropboxOAuth2Flow
from dropbox.oauth import BadRequestException, BadStateException, CsrfException, NotApprovedException, ProviderException

from webapp.model import *
from webapp import db

settings = Blueprint('settings', __name__, template_folder='templates')


@settings.route('/')
@login_required
def index():
    title = 'Настройки'
    try:
        current_user_pref = UserPreferences.query.filter(UserPreferences.user_id==current_user.id).first()
        threshold = current_user_pref.classification_threshold
    except:
        threshold = 0

    # Ограничиваем полученное значение и переводим в целое число:
    if threshold < 1:
        if threshold < 0:
            threshold = 0
        else:
            threshold *= 100
    elif threshold > 100:
        threshold = 100

    threshold = int(threshold)

    dropbox_storage = StorageUsers.query \
                        .filter(StorageUsers.storage_id == 1) \
                        .filter(StorageUsers.global_user_id == current_user.id) \
                        .first()

    if current_user.is_authenticated:
            user = current_user.login
    else:
            user = 'guest'

    context = {
        'title': title,
        'page_title': title,
        'current_user': current_user,
        'user': user,
        'storages': current_user.storageusers,
        'has_dropbox': not(dropbox_storage is None),
        'threshold': threshold,
        }

    return render_template('settings/index.html', context=context, user=user, page_title=title)


@settings.route('/dropbox-delete')
@login_required
def dropbox_delete():
    # TODO: А может сюда передать StorageUsers.id?
    db.session.query(StorageUsers) \
            .filter(StorageUsers.global_user_id == current_user.id) \
            .filter(StorageUsers.storage_id == 1) \
            .delete(synchronize_session='fetch')
    db.session.commit()

    return redirect(url_for('settings.index'))


def get_dropbox_auth_flow(web_app_session):
    redirect_uri = url_for('settings.dropbox_auth_finish', _external=True)
    return DropboxOAuth2Flow(
            app.config["DROPBOX_APP_KEY"],
            app.config["DROPBOX_APP_SECRET"],
            redirect_uri, web_app_session, "dropbox-auth-csrf-token")


@settings.route('/dropbox-auth-start')
@login_required
def dropbox_auth_start():
    authorize_url = get_dropbox_auth_flow(session).start()
    return redirect(authorize_url)


@settings.route('/dropbox-auth-finish')
@login_required
def dropbox_auth_finish():
    try:
        oauth_result =  get_dropbox_auth_flow(session).finish(request.args)
    except BadRequestException as e:
        http_status(400)
    except BadStateException as e:
        redirect(url_for('settings.dropbox_auth_start'))
    except CsrfException as e:
        http_status(403)
    except NotApprovedException as e:
        flash('Not approved?  Why not?')
        return redirect(url_for('settings.index'))
    except ProviderException as e:
        app.logger.error("Auth error: %s" % (e,))
        http_status(403)

    storage = StorageUsers(
            name='Dropbox',
            credentials=oauth_result.access_token,
            storage_id=1,
            global_user_id=current_user.id)
    db.session.add(storage)
    db.session.commit()
    db.session.refresh(storage)

    from webapp.pa_tasks.celery import sync_file_list
    sync_file_list.delay(storage.id)

    return redirect(url_for('settings.index'))


@settings.route('/yadisk-auth-start')
@login_required
def yadisk_auth_start():
    return redirect('#')


@settings.route('/nas-auth-start')
@login_required
def nas_auth_start():
    return redirect('#')


@settings.route('/update_threshold')
@login_required
def update_threshold():
    
    new_threshold = request.args.get('threshold', 0, type=int)
    new_threshold /= 100
    print(new_threshold)
    
    # Если запись с настройками в БД есть - обновляем
    try:
        current_user_pref = UserPreferences.query.filter(UserPreferences.user_id==current_user.id).first()
        current_user_pref.classification_threshold = new_threshold

        db.session.commit()

        print('New threshold: {}'.format(new_threshold))
        #return jsonify(result=new_threshold)

    # У пользователя еще нет настроек в БД, добавляем
    except:
        new_user_pref = UserPreferences(user_id=current_user.id, classification_threshold = new_threshold)

        db.session.add(new_user_pref)
        db.session.commit()

            #return jsonify(result='error')
    return jsonify(result=new_threshold)
