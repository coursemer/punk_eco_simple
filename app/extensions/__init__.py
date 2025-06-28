"""Extensions Flask pour l'application Punk Eco.

Ce module initialise toutes les extensions utilisées par l'application Flask.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
cache = Cache()
cors = CORS()
jwt = JWTManager()

def init_extensions(app):
    """Initialise toutes les extensions avec l'application Flask.
    
    Args:
        app: L'application Flask
    """
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)
    
    # Configuration supplémentaire pour Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
