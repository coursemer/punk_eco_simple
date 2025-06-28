"""
Package d'authentification pour l'application Punk Eco.
"""

from flask import Blueprint

# Créer un Blueprint pour l'authentification
auth_bp = Blueprint('auth', __name__)
