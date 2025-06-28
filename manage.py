#!/usr/bin/env python
"""
Script de gestion pour l'application Punk Eco.
Permet d'exécuter des commandes de gestion comme les migrations de base de données.
"""

import os
from flask import Flask
from flask_migrate import Migrate
from app import create_app, db
from app.models import *  # Importe tous les modèles pour les migrations

# Créer l'application Flask
app = create_app(os.getenv('FLASK_ENV', 'development').capitalize())
migrate = Migrate(app, db)

def register_commands(app: Flask):
    """Enregistre les commandes personnalisées pour l'application."""
    @app.cli.command('shell')
    def shell():
        """Ouvre un shell interactif avec le contexte de l'application."""
        import code
        from flask.globals import _app_ctx_stack
        app = _app_ctx_stack.top.app
        ctx = {}
        ctx.update(app.make_shell_context())
        code.interact(local=ctx)

# Enregistrer les commandes personnalisées
register_commands(app)

if __name__ == '__main__':
    app.run(debug=True)
