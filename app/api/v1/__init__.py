"""
Module pour la version 1 de l'API.
Contient les endpoints principaux de l'API v1.
"""

from flask import jsonify, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.user import User
from ...extensions import db

# Import des routes d'API
from . import auth, users, resources  # noqa: F401

def register_routes(api_bp):
    """Enregistre les routes de l'API v1.
    
    Args:
        api_bp: Le blueprint de l'API
    """
    # Endpoint racine de l'API v1
    @api_bp.route('')
    def index():
        """Endpoint racine de l'API v1."""
        return jsonify({
            'name': 'Punk Eco API',
            'version': '1.0',
            'status': 'active',
            'documentation': '/api/v1/docs'
        })
    
    # Endpoint de documentation
    @api_bp.route('/docs')
    def docs():
        """Redirige vers la documentation de l'API."""
        return jsonify({
            'swagger': '/api/v1/docs/swagger.json',
            'redoc': '/api/v1/docs/redoc',
            'swagger_ui': '/api/v1/docs/swagger-ui'
        })
    
    # Endpoint pour obtenir les informations de l'utilisateur actuel
    @api_bp.route('/me', methods=['GET'])
    @jwt_required()
    def get_current_user():
        """Récupère les informations de l'utilisateur connecté."""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
            
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        })
    
    # Endpoint de test d'authentification
    @api_bp.route('/protected', methods=['GET'])
    @jwt_required()
    def protected():
        """Endpoint protégé pour tester l'authentification JWT."""
        current_user_id = get_jwt_identity()
        return jsonify({
            'message': f'Accès autorisé pour l\'utilisateur {current_user_id}'
        }), 200
