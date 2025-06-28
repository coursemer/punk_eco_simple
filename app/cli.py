"""
Module de gestion des commandes en ligne de commande pour Punk Eco.
"""

import click
from flask.cli import with_appcontext
from .extensions import db
from .models.user import User


def init_app(app):
    """Initialise les commandes CLI avec l'application Flask."""
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
        email: Adresse email de l'administrateur
        password: Mot de passe de l'administrateur
    """
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


def main():
    """Point d'entrée principal pour les commandes CLI."""
    from .app import create_app
    app = create_app()
    with app.app_context():
        init_app(app)
        app.cli()


if __name__ == '__main__':
    main()
