"""API Blueprint pour l'application Punk Eco.

Ce module définit les routes API pour accéder aux données de l'application.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

# Créer le blueprint
api_bp = Blueprint('api', __name__)

def init_app(app):
    """Initialise les routes API avec l'application Flask."""
    from . import auth, economy, users  # noqa
    
    # Enregistrer les blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

@api_bp.route('/status')
@jwt_required()
def status():
    """Endpoint de statut de l'API."""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'service': 'Punk Eco API'
    })
