"""Décorateurs utilitaires pour l'application."""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models.user import User

def admin_required(fn):
    """Vérifie que l'utilisateur est un administrateur."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({
                'status': 'error',
                'message': 'Accès refusé. Droits administrateur requis.'
            }), 403
            
        return fn(*args, **kwargs)
    return wrapper

def role_required(roles):
    """Vérifie que l'utilisateur a l'un des rôles requis."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or user.role not in roles:
                return jsonify({
                    'status': 'error',
                    'message': f'Accès refusé. Rôle requis: {", ".join(roles)}'
                }), 403
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator
