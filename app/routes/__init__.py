"""
Initialisation des routes de l'application.
"""

from flask import Blueprint

# Créer un Blueprint pour les routes principales
main = Blueprint('main', __name__)

# Importer les routes après la création du Blueprint pour éviter les importations circulaires
from . import views
