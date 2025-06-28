"""
Commandes personnalisées pour l'application Flask.
"""

import click
from flask import current_app
from flask.cli import with_appcontext
from .extensions import db


def init_app(app):
    """Initialise les commandes personnalisées pour l'application."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialise la base de données."""
    # Supprimer toutes les tables existantes
    db.drop_all()
    
    # Créer toutes les tables
    db.create_all()
    
    click.echo('Base de données initialisée avec succès.')


@click.command('create-admin')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin_command(email, password):
    """Crée un utilisateur administrateur.
    
    Args:
        email: Email de l'administrateur
        password: Mot de passe de l'administrateur
    """
    from .models.user import User
    
    # Vérifier si l'utilisateur existe déjà
    if User.query.filter_by(email=email).first():
        click.echo(f'Un utilisateur avec l\'email {email} existe déjà.')
        return
    
    # Créer un nouvel utilisateur administrateur
    admin = User(
        email=email,
        username='admin',
        is_admin=True
    )
    admin.set_password(password)
    
    # Sauvegarder l'utilisateur
    db.session.add(admin)
    db.session.commit()
    
    click.echo(f'Administrateur {email} créé avec succès.')
