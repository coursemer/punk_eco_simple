"""Routes API pour la gestion des utilisateurs."""

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash

from app.models.user import User, db
from app.utils.decorators import admin_required
from . import api_bp

@api_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """Récupère la liste des utilisateurs (admin uniquement)."""
    users = User.query.all()
    return jsonify({
        'status': 'success',
        'data': [{
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        } for user in users]
    }), 200

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Récupère les informations d'un utilisateur spécifique."""
    current_user_id = get_jwt_identity()
    
    # Un utilisateur ne peut voir que son propre profil, sauf s'il est admin
    if current_user_id != user_id and not User.query.get(current_user_id).is_admin:
        return jsonify({'message': 'Accès non autorisé'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify({
        'status': 'success',
        'data': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    }), 200

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Met à jour les informations d'un utilisateur."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Un utilisateur ne peut mettre à jour que son propre profil, sauf admin
    if current_user_id != user_id and not current_user.is_admin:
        return jsonify({'message': 'Accès non autorisé'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Mise à jour des champs autorisés
    if 'username' in data:
        user.username = data['username']
    
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Cet email est déjà utilisé'}), 400
        user.email = data['email']
    
    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'])
    
    # Seul un admin peut modifier le statut admin
    if 'is_admin' in data and current_user.is_admin:
        user.is_admin = bool(data['is_admin'])
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Utilisateur mis à jour avec succès',
        'data': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'is_admin': user.is_admin
        }
    }), 200

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Supprime un utilisateur (admin uniquement)."""
    user = User.query.get_or_404(user_id)
    
    # Empêcher l'auto-suppression
    current_user_id = get_jwt_identity()
    if user.id == current_user_id:
        return jsonify({'message': 'Vous ne pouvez pas supprimer votre propre compte'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Utilisateur supprimé avec succès'
    }), 200
