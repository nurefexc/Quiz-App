import os
from flask import Flask, request, session, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel, lazy_gettext as _l
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()

def get_locale():
    from flask import request, session, current_app
    if 'language' in session and session['language'] in current_app.config['LANGUAGES']:
        return session['language']
    return request.accept_languages.best_match(current_app.config['LANGUAGES']) or 'en'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = _l('Please log in to access this page.')
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    babel.init_app(app, locale_selector=get_locale)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.quiz import bp as quiz_bp
    app.register_blueprint(quiz_bp, url_prefix='/quiz')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app
