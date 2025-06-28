"""Blueprint pour la gestion de l'authentification.

Ce module contient les routes pour la connexion, l'inscription, la déconnexion,
et la gestion du compte utilisateur.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import logout_user, login_required, current_user

# Créer le blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Gère la connexion des utilisateurs."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Logique de connexion
        pass
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Gère l'inscription des nouveaux utilisateurs."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Logique d'inscription
        pass
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnecte l'utilisateur actuel."""
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'success')
    return redirect(url_for('main.index'))
