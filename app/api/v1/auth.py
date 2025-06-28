"""
Module d'authentification de l'API v1.
Contient les endpoints pour l'inscription, la connexion, et la gestion des jetons.
"""

from flask import jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import timedelta
import re
from ...models.user import User
from ...extensions import db

def init_auth_routes(api_bp):
    """Initialise les routes d'authentification.
    
    Args:
        api_bp: Le blueprint de l'API
    """
    @api_bp.route('/auth/register', methods=['POST'])
    def register():
        """Enregistre un nouvel utilisateur."""
        data = request.get_json()
        
        # Validation des données
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'error': 'Email et mot de passe requis',
                'status': 'error'
            }), 400
        
        # Validation de l'email
        if not re.match(r'[^@]+@[^@]+\.[^@]+', data['email']):
            return jsonify({
                'error': 'Format d\'email invalide',
                'status': 'error'
            }), 400
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'error': 'Un compte avec cet email existe déjà',
                'status': 'error'
            }), 409
        
        # Créer un nouvel utilisateur
        try:
            user = User(
                username=data.get('username', data['email'].split('@')[0]),
                email=data['email'],
                password=data['password']
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Créer les jetons d'accès
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return jsonify({
                'message': 'Compte créé avec succès',
                'status': 'success',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Erreur lors de la création du compte: {str(e)}')
            return jsonify({
                'error': 'Une erreur est survenue lors de la création du compte',
                'status': 'error'
            }), 500
    
    @api_bp.route('/auth/login', methods=['POST'])
    def login():
        """Connecte un utilisateur et renvoie des jetons JWT."""
        data = request.get_json()
        
        # Validation des données
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'error': 'Email et mot de passe requis',
                'status': 'error'
            }), 400
        
        # Trouver l'utilisateur
        user = User.query.filter_by(email=data['email']).first()
        
        # Vérifier le mot de passe
        if not user or not user.check_password(data['password']):
            return jsonify({
                'error': 'Email ou mot de passe incorrect',
                'status': 'error'
            }), 401
        
        # Vérifier si le compte est actif
        if not user.is_active:
            return jsonify({
                'error': 'Ce compte est désactivé',
                'status': 'error'
            }), 403
        
        # Mettre à jour la dernière connexion
        user.update_last_login()
        
        # Créer les jetons d'accès
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Connexion réussie',
            'status': 'success',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    @api_bp.route('/auth/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        """Rafraîchit un jeton d'accès expiré."""
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_token,
            'status': 'success'
        })
    
    @api_bp.route('/auth/logout', methods=['POST'])
    @jwt_required()
    def logout():
        """Déconnecte l'utilisateur et invalide le jeton."""
        # Dans une implémentation réelle, vous voudrez peut-être ajouter le jeton à une liste noire
        jti = get_jwt()['jti']
        # Ici, vous pouvez stocker le jti dans une base de données ou Redis pour l'invalider
        
        return jsonify({
            'message': 'Déconnexion réussie',
            'status': 'success'
        }), 200
    
    @api_bp.route('/auth/me', methods=['GET'])
    @jwt_required()
    def get_me():
        """Récupère les informations de l'utilisateur connecté."""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
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
