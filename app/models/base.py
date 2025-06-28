"""
Modèle de base pour tous les modèles de l'application.
"""

from datetime import datetime
from .. import db

class BaseModel(db.Model):
    """Classe de base pour tous les modèles de l'application."""
    
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def save(self):
        """Enregistre l'instance dans la base de données."""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Supprime l'instance de la base de données."""
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        """Met à jour les champs de l'instance avec les valeurs fournies."""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    @classmethod
    def get_by_id(cls, id):
        """Récupère une instance par son ID."""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """Récupère toutes les instances du modèle."""
        return cls.query.all()
