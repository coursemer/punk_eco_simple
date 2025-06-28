"""Blueprint pour les routes principales de l'application.

Ce module contient les routes de base comme la page d'accueil, la page à propos, etc.
"""

from flask import Blueprint, render_template, current_app
from flask_login import login_required

# Créer le blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Affiche la page d'accueil."""
    return render_template('main/index.html')

@main_bp.route('/about')
def about():
    """Affiche la page À propos."""
    return render_template('main/about.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Affiche le tableau de bord utilisateur."""
    return render_template('main/dashboard.html')

@main_bp.route('/economy')
@login_required
def economy_dashboard():
    """Affiche le tableau de bord économique marocain."""
    # Vérifier si le tableau de bord est activé dans la configuration
    if not current_app.config.get('ENABLE_MA_ECONOMY_DASHBOARD', False):
        return render_template('errors/404.html'), 404
    
    return render_template('ma_economy/dashboard.html')
