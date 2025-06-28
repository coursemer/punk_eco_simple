"""
Modèle utilisateur pour l'authentification.
"""

from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin as FlaskLoginUserMixin
from flask_security import (
    SQLAlchemyUserDatastore,
    RoleMixin as SecurityRoleMixin
)

# Implémentation minimale des fonctionnalités nécessaires de SecurityUserMixin
class SecurityUserMixin:
    """Implémentation minimale des fonctionnalités nécessaires de SecurityUserMixin."""
    
    # Ces propriétés sont nécessaires pour Flask-Security-Too
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    active = db.Column(db.Boolean, default=True)
    
    # Ces méthodes sont nécessaires pour Flask-Security-Too
    def get_security_payload(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username
        }

# Utiliser SecurityUserMixin qui inclut déjà les fonctionnalités de base nécessaires
from ..extensions import db

# Table de liaison pour la relation many-to-many entre User et Role
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
)


class Role(db.Model, SecurityRoleMixin):
    """Modèle pour les rôles des utilisateurs."""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    @classmethod
    def insert_roles(cls):
        """Insère les rôles par défaut s'ils n'existent pas."""
        roles = {
            'admin': 'Administrateur avec accès complet',
            'user': 'Utilisateur standard',
            'editor': 'Éditeur avec des droits limités',
            'viewer': 'Lecture seule',
            'api': 'Accès API uniquement'
        }
        
        for name, description in roles.items():
            role = cls.query.filter_by(name=name).first()
            if role is None:
                role = cls(name=name, description=description)
                db.session.add(role)
        db.session.commit()


class User(FlaskLoginUserMixin, db.Model, SecurityUserMixin):
    """Modèle utilisateur pour l'authentification."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer, default=0)
    
    # Relation avec les rôles
    roles = db.relationship(
        'Role', 
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.set_password(kwargs.get('password', ''))
    
    def set_password(self, password):
        """Définit le mot de passe de l'utilisateur."""
        if password:
            self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie si le mot de passe est correct."""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Retourne l'identifiant de l'utilisateur (nécessaire pour Flask-Login)."""
        return str(self.id)
    
    def has_role(self, role_name):
        """Vérifie si l'utilisateur a le rôle spécifié."""
        return self.roles.filter(Role.name == role_name).first() is not None
    
    def add_role(self, role_name):
        """Ajoute un rôle à l'utilisateur."""
        if not self.has_role(role_name):
            role = Role.query.filter_by(name=role_name).first()
            if role:
                self.roles.append(role)
                db.session.add(self)
                db.session.commit()
    
    def remove_role(self, role_name):
        """Supprime un rôle de l'utilisateur."""
        if self.has_role(role_name):
            role = Role.query.filter_by(name=role_name).first()
            if role:
                self.roles.remove(role)
                db.session.commit()
    
    def get_roles(self):
        """Retourne la liste des noms des rôles de l'utilisateur."""
        return [role.name for role in self.roles]
    
    def has_permission(self, permission_name):
        """Vérifie si l'utilisateur a la permission spécifiée.
        
        Note: Cette méthode peut être étendue pour gérer des permissions plus complexes.
        """
        # Pour l'instant, on vérifie simplement si l'utilisateur est admin
        return self.is_admin or self.has_role('admin')
    
    def update_last_login(self, ip_address):
        """Met à jour les informations de connexion de l'utilisateur."""
        self.last_login_at = self.current_login_at or datetime.utcnow()
        self.current_login_at = datetime.utcnow()
        self.last_login_ip = self.current_login_ip
        self.current_login_ip = ip_address
        self.login_count = (self.login_count or 0) + 1
        db.session.commit()
    
    @classmethod
    def create_user(cls, email, username, password, roles=None, **kwargs):
        """Crée un nouvel utilisateur avec les rôles spécifiés."""
        user = cls(email=email, username=username, **kwargs)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Pour obtenir l'ID de l'utilisateur
        
        # Ajout des rôles
        if roles:
            for role_name in roles:
                user.add_role(role_name)
        
        db.session.commit()
        return user
    
    def __repr__(self):
        return f'<User {self.username} ({self.email})>'


# Initialisation du user_datastore pour Flask-Security-Too
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

class User(UserMixin, db.Model):
    """Modèle utilisateur pour l'authentification."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer, default=0)
    
    # Relation avec les rôles
    roles = db.relationship(
        'Role', 
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.set_password(kwargs.get('password', ''))
    
    def set_password(self, password):
        """Définit le mot de passe de l'utilisateur."""
        if password:
            self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie si le mot de passe est correct."""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Retourne l'identifiant de l'utilisateur (nécessaire pour Flask-Login)."""
        return str(self.id)
    
    def has_role(self, role_name):
        """Vérifie si l'utilisateur a le rôle spécifié."""
        return self.roles.filter(Role.name == role_name).first() is not None
    
    def add_role(self, role_name):
        """Ajoute un rôle à l'utilisateur."""
        if not self.has_role(role_name):
            role = Role.query.filter_by(name=role_name).first()
            if role:
                self.roles.append(role)
                db.session.add(self)
                db.session.commit()
    
    def remove_role(self, role_name):
        """Supprime un rôle de l'utilisateur."""
        if self.has_role(role_name):
            role = Role.query.filter_by(name=role_name).first()
            if role:
                self.roles.remove(role)
                db.session.commit()
    
    def get_roles(self):
        """Retourne la liste des noms des rôles de l'utilisateur."""
        return [role.name for role in self.roles]
    
    def has_permission(self, permission_name):
        """Vérifie si l'utilisateur a la permission spécifiée.
        
        Note: Cette méthode peut être étendue pour gérer des permissions plus complexes.
        """
        # Pour l'instant, on vérifie simplement si l'utilisateur est admin
        return self.is_admin or self.has_role('admin')
    
    def update_last_login(self, ip_address):
        """Met à jour les informations de connexion de l'utilisateur."""
        self.last_login_at = self.current_login_at or datetime.utcnow()
        self.current_login_at = datetime.utcnow()
        self.last_login_ip = self.current_login_ip
        self.current_login_ip = ip_address
        self.login_count = (self.login_count or 0) + 1
        db.session.commit()
    
    @classmethod
    def create_user(cls, email, username, password, roles=None, **kwargs):
        """Crée un nouvel utilisateur avec les rôles spécifiés."""
        user = cls(email=email, username=username, password=password, **kwargs)
        db.session.add(user)
        db.session.flush()  # Pour obtenir l'ID de l'utilisateur
        
        # Ajout des rôles
        if roles:
            for role_name in roles:
                user.add_role(role_name)
        
        db.session.commit()
        return user
    
    def __repr__(self):
        return f'<User {self.username} ({self.email})>'
