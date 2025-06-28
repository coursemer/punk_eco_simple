"""
Configuration settings for Punk Eco application.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Directory paths
BASEDIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASEDIR)
INSTANCE_FOLDER_PATH = os.path.join(ROOT_DIR, 'instance')

# Create instance folder if it doesn't exist
os.makedirs(INSTANCE_FOLDER_PATH, exist_ok=True)

class Config:
    """Base configuration common to all environments."""
    # Application settings
    APP_NAME = 'Punk Eco'
    APP_VERSION = '1.0.0'
    
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-this-in-production')
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'change-this-in-production')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(INSTANCE_FOLDER_PATH, "app.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
    }
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json', 'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Cache settings
    CACHE_TYPE = 'simple'  # Use 'redis' or 'memcached' in production
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@example.com')
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-this-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # Flask-Login settings
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    SESSION_PROTECTION = 'strong'
    
    # Pagination settings
    ITEMS_PER_PAGE = 20
    
    # API settings
    API_TITLE = 'Punk Eco API'
    API_VERSION = '1.0'
    OPENAPI_VERSION = '3.0.3'
    OPENAPI_URL_PREFIX = '/api'
    OPENAPI_SWAGGER_UI_PATH = '/docs'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'


class DevelopmentConfig(Config):
    """Configuration for development environment."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        f"sqlite:///{os.path.join(INSTANCE_FOLDER_PATH, 'app-dev.db')}")
    SQLALCHEMY_ECHO = True
    
    # Disable caching in development
    CACHE_TYPE = 'null'
    
    # Allow all hosts for development
    CORS_ORIGINS = '*'


class TestingConfig(Config):
    """Configuration for testing environment."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite for testing
    SQLALCHEMY_ECHO = False
    
    # Disable CSRF protection for testing
    WTF_CSRF_ENABLED = False
    
    # Disable mail sending in tests
    MAIL_SUPPRESS_SEND = True
    
    # Use a different upload folder for tests
    UPLOAD_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'test_uploads')
    
    # Use a different secret key for testing
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'


class ProductionConfig(Config):
    """Configuration for production environment."""
    DEBUG = False
    TESTING = False
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable must be set in production")
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Disable template auto-reload in production
    TEMPLATES_AUTO_RELOAD = False
    
    # Use Redis or Memcached for caching in production
    CACHE_TYPE = 'redis'  # or 'memcached'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Required settings for production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
        
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY environment variable must be set in production")


def get_config():
    """Get the appropriate configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    
    configs = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
    }
    
    return configs.get(env, DevelopmentConfig)

# Available configurations
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Current configuration
ConfigClass = get_config()

# Initialize upload folder
try:
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    test_upload_folder = os.path.join(INSTANCE_FOLDER_PATH, 'test_uploads')
    os.makedirs(test_upload_folder, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create upload directories: {e}")
