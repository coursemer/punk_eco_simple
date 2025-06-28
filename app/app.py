"""
Module principal de l'application Punk Eco.
Contient la factory pour créer l'application Flask.
"""

import os
from flask import Flask, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime

# Importer les extensions
from .extensions import db, migrate, login_manager, cache, mail, cors, init_extensions

# Importer la configuration
from .config.settings import config

def create_app(config_name=None):
    """Crée et configure l'application Flask.
    
    Args:
        config_name: Nom de la configuration à utiliser (development, testing, production, etc.)
    
    Returns:
        app: Instance de l'application Flask configurée
    """
    # Créer l'application Flask
    app = Flask(__name__,
                static_url_path='/static',
                static_folder='static',
                template_folder='templates')
    
    # Ajouter des filtres personnalisés
    @app.template_filter('format_date')
    def format_date_filter(date, format='%d/%m/%Y'):
        """Formatte une date selon le format spécifié.
        
        Args:
            date: Objet date ou datetime à formater
            format: Format de sortie (par défaut: '%%d/%%m/%%Y')
            
        Returns:
            str: Date formatée ou chaîne vide si la date est None
        """
        if date is None:
            return ''
        return date.strftime(format)
    
    @app.template_filter('format_number')
    def format_number_filter(number, decimals=0, decimal_sep=',', thousand_sep=' '):
        """Formate un nombre avec des séparateurs de milliers et de décimales.
        
        Args:
            number: Nombre à formater
            decimals: Nombre de décimales à afficher (par défaut: 0)
            decimal_sep: Séparateur décimal (par défaut: ',')
            thousand_sep: Séparateur de milliers (par défaut: espace insécable)
            
        Returns:
            str: Nombre formaté ou chaîne vide si le nombre est None
        """
        if number is None:
            return ''
            
        try:
            # Convertir en float pour gérer les chaînes
            num = float(number)
            
            # Formater le nombre avec les séparateurs
            parts = f"{num:,.{decimals}f}".split(".")
            
            # Remplacer les séparateurs
            formatted = parts[0].replace(",", "_").replace(".", "_").replace("_", thousand_sep)
            
            # Ajouter les décimales si nécessaire
            if decimals > 0:
                if len(parts) > 1:
                    formatted += decimal_sep + parts[1].ljust(decimals, '0')
                else:
                    formatted += decimal_sep + '0' * decimals
            
            return formatted
        except (ValueError, TypeError):
            return str(number)
    
    # Charger la configuration
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Charger la configuration appropriée
    app.config.from_object(config[config_name])
    
    # S'assurer que le dossier d'upload existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialiser les extensions
    init_extensions(app)
    
    # Enregistrer les commandes personnalisées
    from . import commands
    commands.init_app(app)
    
    # Enregistrer les blueprints
        # Enregistrer les blueprints
    from .routes import main as main_blueprint
    from .auth import auth_bp
    from .api import api_bp
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Importer les modèles pour s'assurer qu'ils sont enregistrés avec SQLAlchemy
    from .models import user  # noqa: F401
    
    # Créer les tables de la base de données
    with app.app_context():
        db.create_all()
    
    # Enregistrer les routes personnalisées
    register_routes(app)
    
    # Injecter des variables globales dans tous les templates
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}
    
    return app


def register_routes(app):
    """Enregistre les routes personnalisées de l'application."""
    
    @app.route('/')
    def index():
        """Page d'accueil de l'application."""
        return {'message': 'Bienvenue sur l\'API Punk Eco!', 'status': 'success'}
    
    @app.route('/api/status')
    def api_status():
        """Vérifie l'état de l'API."""
        return {
            'status': 'en ligne',
            'version': '1.0.0',
            'environment': app.config.get('ENV', 'production')
        }
    
    @app.route('/api/profile')
    @login_required
    def user_profile():
        """Récupère le profil de l'utilisateur connecté."""
        return {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'created_at': current_user.created_at
        }
    
    @app.route('/api/health')
    def health_check():
        """Vérifie la santé de l'application."""
        try:
            # Vérifier la connexion à la base de données
            db.session.execute('SELECT 1')
            return {
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            }, 200
        except Exception as e:
            return {
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }, 500
    
    # Gestion des erreurs
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Ressource non trouvée', 'status': 'error'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Erreur interne du serveur', 'status': 'error'}, 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Accès non autorisé', 'status': 'error'}, 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return {'error': 'Authentification requise', 'status': 'error'}, 401
    
    # Route pour tester les erreurs 500
    @app.route('/test-500')
    def test_500():
        # Cette route est utilisée pour tester la gestion des erreurs 500
        # Ne pas utiliser en production
        if app.debug or app.testing:
            1 / 0  # Génère une erreur de division par zéro
        return {'message': 'Cette route est désactivée en production'}, 403
