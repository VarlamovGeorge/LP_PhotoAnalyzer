from flask import Blueprint, render_template, request, redirect, url_for, session
from flask import current_app as app
from flask_login import current_user, login_required

from dropbox import DropboxOAuth2Flow
from dropbox.oauth import BadRequestException, BadStateException, CsrfException, NotApprovedException, ProviderException

from webapp.model import Users, StorageUsers 
from webapp import db

settings = Blueprint('settings', __name__, template_folder='templates')

@settings.route('/')
@login_required
def index():
    print(current_user.storageusers)

    context = {
        'title' : 'Settings',
        'current_user' : current_user,
        'storages' : current_user.storageusers,
            }
    
    return render_template('settings/index.html', context=context)


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
        return redirect(url_for('settings'))
    except ProviderException as e:
        app.logger.error("Auth error: %s" % (e,))
        http_status(403)

#    print(oauth_result.access_token)
#    flash('Access token: %s' % oauth_result.access_token)

    storage = StorageUsers(
            name='Dropbox',
            credentials=oauth_result.access_token,
            storage_id=1,
            global_user_id=current_user.id)
    db.session.add(storage)
    db.session.commit()

    return redirect(url_for('settings.index'))

