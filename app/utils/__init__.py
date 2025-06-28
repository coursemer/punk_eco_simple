"""
Utilitaires pour l'application Punk Eco.

Ce package contient des fonctions utilitaires utilisées dans toute l'application.
"""

# Import des utilitaires
from .dash_utils import (
    register_dashapp,
    create_navbar,
    create_footer
)

__all__ = [
    'register_dashapp',
    'create_navbar',
    'create_footer',
    'create_loading_components'
]
