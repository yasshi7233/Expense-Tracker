import os
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).resolve().parent.parent
load_dotenv(basedir / '.env')

def normalize_database_url(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql+psycopg2://', 1)
    if url.startswith('postgresql://'):
        return url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    return url

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-insecure-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database URL compatibility
    # Render and older platforms supply 'postgres://' or 'postgresql://'.
    # SQLAlchemy 2.x defaults 'postgresql://' to the 'psycopg' (psycopg3) driver.
    # Since our production driver is 'psycopg2' (via psycopg2-binary), normalize both prefixes
    # to 'postgresql+psycopg2://' so SQLAlchemy explicitly uses psycopg2.
    SQLALCHEMY_DATABASE_URI = normalize_database_url(os.environ.get('DATABASE_URL')) or f"sqlite:///{basedir / 'expense.db'}"
    
    # Cookie & session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1')
    WTF_CSRF_ENABLED = True

    @classmethod
    def init_app(cls, app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    @classmethod
    def init_app(cls, app):
        if app.config.get('TESTING'):
            return
        raw_db = os.environ.get('DATABASE_URL')
        if not raw_db:
            raise ValueError(
                "CRITICAL CONFIGURATION ERROR: DATABASE_URL environment variable is required in production mode. "
                "The application will not start without a valid PostgreSQL database URL to prevent data loss on ephemeral filesystems."
            )
        # Ensure app.config reflects normalized database url when set in environment at runtime
        app.config['SQLALCHEMY_DATABASE_URI'] = normalize_database_url(raw_db)

        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key or secret_key == 'dev-insecure-secret-key-change-in-production':
            raise ValueError(
                "CRITICAL CONFIGURATION ERROR: A secure SECRET_KEY environment variable is required in production mode."
            )
        app.config['SECRET_KEY'] = secret_key

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
