"""
Configuration de l'application Punk Eco.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../../.env'))

class Config:
    """Configuration de base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-pour-le-developpement'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration de l'upload
    UPLOAD_FOLDER = os.path.join(basedir, '..', 'instance', 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Configuration de la base de données par défaut
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'app.db')
    
    # Configuration de la pagination
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Configuration pour le développement."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Configuration pour les tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Configuration pour la production."""
    DEBUG = False
    # Utiliser une base de données PostgreSQL en production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/punk_eco'


# Dictionnaire des configurations disponibles
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
