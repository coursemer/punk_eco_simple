"""
Point d'entrée WSGI pour l'application Punk Eco.
"""

import os
import sys

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Créer l'application Flask
app = create_app(os.getenv('FLASK_ENV', 'development').lower())

# Cette condition permet d'exécuter l'application avec 'python wsgi.py'
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
