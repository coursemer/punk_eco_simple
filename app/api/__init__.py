"""
Package pour l'API de l'application Punk Eco.
Contient les blueprints et les routes de l'API.
"""

from flask import Blueprint, jsonify
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity

# Créer le blueprint principal de l'API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Importer et configurer la version 1 de l'API
from .v1 import register_routes as register_v1_routes

# Créer et configurer le blueprint pour la version 1 de l'API
v1_bp = Blueprint('v1', __name__, url_prefix='/v1')
register_v1_routes(v1_bp)

# Enregistrer le blueprint de la version 1
api_bp.register_blueprint(v1_bp)

# Endpoint racine de l'API
@api_bp.route('')
def index():
    """Endpoint racine de l'API."""
    return jsonify({
        'name': 'Punk Eco API',
        'version': '1.0.0',
        'status': 'active',
        'documentation': '/api/docs',
        'versions': {
            'v1': '/api/v1'
        }
    })

# Endpoint de documentation
@api_bp.route('/docs')
def docs():
    """Redirige vers la documentation de l'API."""
    return jsonify({
        'swagger': '/api/docs/swagger.json',
        'redoc': '/api/docs/redoc',
        'swagger_ui': '/api/docs/swagger-ui',
        'status': 'success'
    })

# Fonction utilitaire pour vérifier les rôles
def role_required(*roles):
    """Décorateur pour vérifier les rôles de l'utilisateur."""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            from ...models.user import User
            user = User.query.get(current_user_id)
            
            if not user or not user.is_active:
                return jsonify({
                    'error': 'Accès non autorisé',
                    'status': 'error'
                }), 403
                
            if roles and not any(user.has_role(role) for role in roles):
                return jsonify({
                    'error': 'Permissions insuffisantes',
                    'status': 'error'
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Exporter les éléments principaux
__all__ = ['api_bp', 'role_required']
