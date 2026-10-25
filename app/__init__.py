import os
from pathlib import Path
from flask import Flask
from app.config import config
from app.extensions import db, migrate, login_manager, csrf
from app.core.errors import register_error_handlers

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    # Configure root-level static folder and app/templates folder using Path(__file__).resolve()
    base_dir = Path(__file__).resolve().parent.parent
    static_dir = str(base_dir / 'static')
    template_dir = str(Path(__file__).resolve().parent / 'templates')

    app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
    app.config.from_object(config[config_name])

    # Jinja globals
    app.jinja_env.globals['zip'] = zip

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.transactions import transactions_bp
    from app.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='')
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    register_error_handlers(app)

    return app
