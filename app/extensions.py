"""
Initialisation des extensions Flask.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_caching import Cache
from flask_mail import Mail
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'
cache = Cache()
mail = Mail()
cors = CORS()
scheduler = BackgroundScheduler()

@login_manager.user_loader
def load_user(user_id):
    """Charge un utilisateur à partir de l'ID stocké dans la session."""
    from .models import User
    return User.query.get(int(user_id))

def init_extensions(app):
    """Initialise les extensions avec l'application Flask.
    
    Args:
        app: L'application Flask
    """
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    
    # Initialiser le planificateur de tâches en production
    if app.config.get('ENV') == 'production' and not scheduler.running:
        from ..tasks import init_scheduler
        init_scheduler(app)
