"""Routes d'authentification de l'API."""

from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash

from app.models.user import User
from . import api_bp

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Authentifie un utilisateur et retourne un token JWT."""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email et mot de passe requis'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Identifiants invalides'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({
        'access_token': access_token,
        'user_id': user.id,
        'email': user.email,
        'is_admin': user.is_admin
    }), 200

@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Récupère les informations de l'utilisateur connecté."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'Utilisateur non trouvé'}), 404
    
    return jsonify({
        'user_id': user.id,
        'email': user.email,
        'username': user.username,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat()
    }), 200
