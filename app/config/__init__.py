"""
Configuration de l'application Punk Eco.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '..', '.env'))


class Config:
    """Configuration de base commune à tous les environnements."""
    # Clé secrète pour les sessions et les tokens CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-pour-le-developpement'
    
    # Désactiver le suivi des modifications de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration de l'upload
    UPLOAD_FOLDER = os.path.join(basedir, '..', 'instance', 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Configuration du cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Configuration de l'email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@example.com')
    
    # Configuration CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(basedir, '..', 'instance', 'app-dev.db')}"
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Configuration pour les tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Utilise une base de données en mémoire pour les tests
    WTF_CSRF_ENABLED = False  # Désactive la protection CSRF pour faciliter les tests


class ProductionConfig(Config):
    """Configuration pour la production."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(basedir, '..', 'instance', 'app-prod.db')}"
    
    # Forcer l'utilisation de HTTPS en production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Désactiver le débogage des templates
    TEMPLATES_AUTO_RELOAD = False


# Dictionnaire des configurations disponibles
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
