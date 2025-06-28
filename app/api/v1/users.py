"""
Module pour la gestion des utilisateurs de l'API v1.
Contient les endpoints pour la gestion des profils utilisateurs.
"""

from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.user import User
from ...extensions import db
from werkzeug.security import generate_password_hash

def init_users_routes(api_bp):
    """Initialise les routes de gestion des utilisateurs.
    
    Args:
        api_bp: Le blueprint de l'API
    """
    @api_bp.route('/users', methods=['GET'])
    @jwt_required()
    def get_users():
        """Récupère la liste des utilisateurs (admin uniquement)."""
        # Vérifier si l'utilisateur est admin
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({
                'error': 'Accès non autorisé',
                'status': 'error'
            }), 403
        
        # Récupérer les paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Requête paginée
        pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
        users = pagination.items
        
        return jsonify({
            'items': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'is_active': u.is_active,
                'is_admin': u.is_admin,
                'created_at': u.created_at.isoformat() if u.created_at else None,
                'last_login': u.last_login.isoformat() if u.last_login else None
            } for u in users],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'status': 'success'
        })
    
    @api_bp.route('/users/<int:user_id>', methods=['GET'])
    @jwt_required()
    def get_user(user_id):
        """Récupère les informations d'un utilisateur spécifique."""
        current_user_id = get_jwt_identity()
        requesting_user = User.query.get(current_user_id)
        
        # L'utilisateur ne peut voir que son propre profil s'il n'est pas admin
        if not requesting_user.is_admin and str(current_user_id) != str(user_id):
            return jsonify({
                'error': 'Accès non autorisé',
                'status': 'error'
            }), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'Utilisateur non trouvé',
                'status': 'error'
            }), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'status': 'success'
        })
    
    @api_bp.route('/users/<int:user_id>', methods=['PUT'])
    @jwt_required()
    def update_user(user_id):
        """Met à jour les informations d'un utilisateur."""
        current_user_id = get_jwt_identity()
        requesting_user = User.query.get(current_user_id)
        
        # Vérifier les permissions
        if not requesting_user.is_admin and str(current_user_id) != str(user_id):
            return jsonify({
                'error': 'Accès non autorisé',
                'status': 'error'
            }), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'Utilisateur non trouvé',
                'status': 'error'
            }), 404
        
        data = request.get_json()
        
        # Mise à jour des champs autorisés
        if 'username' in data and data['username']:
            user.username = data['username']
        
        if 'email' in data and data['email'] and '@' in data['email']:
            # Vérifier si l'email est déjà utilisé
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({
                    'error': 'Cet email est déjà utilisé',
                    'status': 'error'
                }), 400
            user.email = data['email']
        
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        
        # Seul un admin peut modifier ces champs
        if requesting_user.is_admin:
            if 'is_active' in data:
                user.is_active = bool(data['is_active'])
            if 'is_admin' in data:
                user.is_admin = bool(data['is_admin'])
        
        try:
            db.session.commit()
            return jsonify({
                'message': 'Utilisateur mis à jour avec succès',
                'status': 'success',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_active': user.is_active,
                    'is_admin': user.is_admin
                }
            })
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Erreur lors de la mise à jour de l\'utilisateur: {str(e)}')
            return jsonify({
                'error': 'Une erreur est survenue lors de la mise à jour',
                'status': 'error'
            }), 500
    
    @api_bp.route('/users/<int:user_id>', methods=['DELETE'])
    @jwt_required()
    def delete_user(user_id):
        """Supprime un utilisateur (admin uniquement)."""
        current_user_id = get_jwt_identity()
        requesting_user = User.query.get(current_user_id)
        
        # Vérifier si l'utilisateur est admin
        if not requesting_user.is_admin:
            return jsonify({
                'error': 'Accès non autorisé',
                'status': 'error'
            }), 403
        
        # Empêcher l'auto-suppression
        if str(current_user_id) == str(user_id):
            return jsonify({
                'error': 'Vous ne pouvez pas supprimer votre propre compte',
                'status': 'error'
            }), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'Utilisateur non trouvé',
                'status': 'error'
            }), 404
        
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({
                'message': 'Utilisateur supprimé avec succès',
                'status': 'success'
            })
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Erreur lors de la suppression de l\'utilisateur: {str(e)}')
            return jsonify({
                'error': 'Une erreur est survenue lors de la suppression',
                'status': 'error'
            }), 500
