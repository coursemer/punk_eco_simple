"""
Point d'entrée WSGI pour le déploiement de l'application Punk Eco.

Ce module permet de déployer l'application avec un serveur WSGI comme Gunicorn ou uWSGI.
"""

import os
from .app import create_app

# Créer l'application Flask
app = create_app(os.getenv('FLASK_ENV', 'production').capitalize())

# Ce bloc permet d'exécuter l'application avec la commande: python -m app.wsgi
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
