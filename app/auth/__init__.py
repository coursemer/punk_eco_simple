"""
Package d'authentification pour l'application Punk Eco.
"""

from flask import Blueprint
from flask_login import LoginManager

# Créer un Blueprint pour l'authentification
auth_bp = Blueprint('auth', __name__)

# Importer les routes après la création du Blueprint pour éviter les importations circulaires
from . import routes
