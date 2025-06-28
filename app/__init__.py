import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_assets import Environment, Bundle

# Initialisation des extensions
db = SQLAlchemy()
cache = Cache()
cors = CORS()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
jwt = JWTManager()
assets = Environment()

def bad_request(e):
    """Gestionnaire d'erreur 400 personnalisé."""
    return render_template('errors/400.html'), 400

def request_timeout(e):
    """Gestionnaire d'erreur 408 personnalisé."""
    return render_template('errors/408.html'), 408

def payload_too_large(e):
    """Gestionnaire d'erreur 413 personnalisé."""
    return render_template('errors/413.html'), 413

def unauthorized(e):
    """Gestionnaire d'erreur 401 personnalisé."""
    return render_template('errors/401.html'), 401

def forbidden(e):
    """Gestionnaire d'erreur 403 personnalisé."""
    return render_template('errors/403.html'), 403

def method_not_allowed(e):
    """Gestionnaire d'erreur 405 personnalisé."""
    return render_template('errors/405.html'), 405

def page_not_found(e):
    """Gestionnaire d'erreur 404 personnalisé."""
    return render_template('errors/404.html'), 404

def gone(e):
    """Gestionnaire d'erreur 410 personnalisé."""
    return render_template('errors/410.html'), 410

def internal_server_error(e):
    """Gestionnaire d'erreur 500 personnalisé."""
    db.session.rollback()
    return render_template('errors/500.html'), 500

def bad_gateway(e):
    """Gestionnaire d'erreur 502 personnalisé."""
    return render_template('errors/502.html'), 502

def service_unavailable(e):
    """Gestionnaire d'erreur 503 personnalisé."""
    return render_template('errors/503.html', now=datetime.utcnow()), 503

def too_many_requests(e):
    """Gestionnaire d'erreur 429 personnalisé."""
    return render_template('errors/429.html'), 429

def create_app(config_name='development'):
    """Application factory pour créer et configurer l'application Flask."""
    # Création de l'application Flask
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    
    # Chargement de la configuration
    config_class = f'config.{config_name.capitalize()}Config'
    app.config.from_object(config_class)
    
    # Configuration du logging
    configure_logging(app)
    
    # Initialisation des extensions
    initialize_extensions(app)
    
    # Configuration des assets
    configure_assets(app)
    
    # Enregistrement des blueprints
    register_blueprints(app)
    
    # Configuration du contexte de l'application
    with app.app_context():
        # Création des tables de la base de données
        db.create_all()
        
        # Initialisation des données de base
        initialize_database()
        
        # Initialisation du tableau de bord Dash
        from app.dash_apps.ma_economy_dash import init_dash
        app = init_dash(app)
        
        # Initialisation des tâches planifiées
        initialize_scheduled_tasks(app)
    
    # Enregistrement des gestionnaires d'erreurs
    app.register_error_handler(400, bad_request)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(408, request_timeout)
    app.register_error_handler(410, gone)
    app.register_error_handler(413, payload_too_large)
    app.register_error_handler(429, too_many_requests)
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(502, bad_gateway)
    app.register_error_handler(503, service_unavailable)
    
    # Commande CLI pour initialiser la base de données
    @app.cli.command('init-db')
    def init_db_command():
        """Initialise la base de données."""
        db.create_all()
        initialize_database()
        print('Base de données initialisée avec succès.')
    
    # Commande CLI pour exécuter les tâches planifiées
    @app.cli.command('run-tasks')
    def run_tasks_command():
        """Exécute les tâches planifiées."""
        from app.tasks import scheduler
        scheduler.start()
        print('Tâches planifiées démarrées.')
    
    return app

def configure_logging(app):
    """Configure le système de journalisation."""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        # Fichier de log principal
        file_handler = RotatingFileHandler(
            'logs/punk_eco.log',
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        
        # Configuration du logger de l'application
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Démarrage de Punk Eco')

def initialize_extensions(app):
    """Initialise les extensions Flask."""
    # Initialisation des extensions
    db.init_app(app)
    cache.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    assets.init_app(app)
    
    # Configuration de Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

def configure_assets(app):
    """Configure les assets (CSS, JS) avec Flask-Assets."""
    # Bundle pour les fichiers CSS
    css_bundle = Bundle(
        'css/styles.css',
        'css/ma_economy.css',
        filters='cssmin',
        output='gen/packed.css'
    )
    
    # Bundle pour les fichiers JavaScript
    js_bundle = Bundle(
        'js/main.js',
        filters='jsmin',
        output='gen/packed.js'
    )
    
    # Enregistrement des bundles
    assets.register('main_css', css_bundle)
    assets.register('main_js', js_bundle)

def register_blueprints(app):
    """Enregistre les blueprints de l'application."""
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.api import init_app as init_api
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Initialiser le blueprint API avec l'application
    init_api(app)

def initialize_database():
    """Initialise la base de données avec des données par défaut."""
    from app.models.user import User, Role
    
    # Créer les tables si elles n'existent pas
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {e}")
            raise
    
    # Création des rôles par défaut
    Role.insert_roles()
    
    # Création d'un utilisateur admin par défaut si aucun utilisateur n'existe
    if User.query.count() == 0:
        admin_role = Role.query.filter_by(name='Admin').first()
        admin = User(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role=admin_role,
            confirmed=True
        )
        db.session.add(admin)
        db.session.commit()
        print('Utilisateur admin créé avec succès.')

def initialize_scheduled_tasks(app):
    """Initialise les tâches planifiées."""
    from app.tasks import init_scheduler
    
    # Démarrer le planificateur de tâches
    scheduler = init_scheduler(app)
    
    # Démarrer le planificateur si nous ne sommes pas en mode test
    if not app.testing:
        scheduler.start()
        app.logger.info('Planificateur de tâches démarré.')