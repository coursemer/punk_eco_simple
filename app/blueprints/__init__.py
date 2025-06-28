"""Blueprints pour l'application Punk Eco.

Ce package contient les blueprints qui organisent les routes de l'application.
"""

from flask import Blueprint

def register_blueprints(app):
    """Enregistre tous les blueprints avec l'application Flask.
    
    Args:
        app: L'application Flask
    """
    # Importer les blueprints ici pour éviter les importations circulaires
    from .main import main_bp
    from .auth import auth_bp
    from .api import api_bp
    
    # Enregistrer les blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Enregistrer les blueprints spécifiques aux modules
    try:
        from .economy import economy_bp
        app.register_blueprint(economy_bp, url_prefix='/economy')
    except ImportError:
        pass  # Le blueprint n'est pas disponible
