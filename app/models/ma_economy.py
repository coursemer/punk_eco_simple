from datetime import datetime
from ..extensions import db

class EconomicIndicator(db.Model):
    """Modèle pour les indicateurs économiques.
    
    Ce modèle stocke les indicateurs économiques avec leurs métadonnées associées.
    """
    __tablename__ = 'economic_indicators'
    
    id = db.Column(db.Integer, primary_key=True)
    indicator_id = db.Column(db.String(50), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))
    date = db.Column(db.Date, nullable=False, index=True)
    source = db.Column(db.String(200))
    category = db.Column(db.String(50), index=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation avec les métadonnées
    metadata_id = db.Column(db.Integer, db.ForeignKey('indicator_metadata.id'), nullable=True)
    
    def __repr__(self):
        return f"<EconomicIndicator {self.indicator_id}: {self.name} = {self.value} {self.unit} ({self.date})>"


class IndicatorMetadata(db.Model):
    """Métadonnées pour les indicateurs économiques.
    
    Cette classe stocke des informations supplémentaires sur les indicateurs
    qui ne changent pas à chaque mise à jour des données.
    """
    __tablename__ = 'indicator_metadata'
    
    id = db.Column(db.Integer, primary_key=True)
    indicator_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    frequency = db.Column(db.String(50))  # e.g., "daily", "monthly", "quarterly", "yearly"
    source = db.Column(db.String(200))
    last_updated = db.Column(db.DateTime)
    
    # Relation avec les indicateurs
    indicators = db.relationship('EconomicIndicator', backref='metadata_ref', lazy=True)
    
    def __repr__(self):
        return f"<IndicatorMetadata {self.indicator_id}: {self.description[:50]}...>"
    
    @classmethod
    def save_from_dict(cls, data: dict):
        """Sauvegarde les indicateurs à partir d'un dictionnaire.
        
        Args:
            data (dict): Dictionnaire contenant les données des indicateurs à sauvegarder.
                Doit contenir les clés 'date' et 'indicators'.
                La clé 'source' est optionnelle (par défaut: 'unknown').
                Chaque entrée dans 'indicators' doit avoir une clé d'identifiant
                et une valeur contenant au moins 'value'.
        """
        if not data or 'date' not in data or 'indicators' not in data:
            return
            
        date = datetime.strptime(data['date'], "%Y-%m-%d").date()
        source = data.get('source', 'unknown')
        
        for indicator_id, details in data['indicators'].items():
            full_indicator_id = f"{source.lower()}_{indicator_id}"
            
            # Vérifier si l'indicateur existe déjà pour cette date
            exists = cls.query.filter_by(
                indicator_id=full_indicator_id,
                date=date
            ).first()
            
            if not exists:
                # Vérifier s'il existe des métadonnées pour cet indicateur
                metadata = IndicatorMetadata.query.filter_by(
                    indicator_id=full_indicator_id
                ).first()
                
                # Créer les métadonnées si elles n'existent pas
                if not metadata and 'description' in details:
                    metadata = IndicatorMetadata(
                        indicator_id=full_indicator_id,
                        description=details.get('description', ''),
                        frequency=details.get('frequency', 'unknown'),
                        source=source,
                        last_updated=datetime.utcnow()
                    )
                    db.session.add(metadata)
                    db.session.flush()  # Pour obtenir l'ID de la nouvelle métadonnée
                
                # Créer l'indicateur
                indicator = cls(
                    indicator_id=full_indicator_id,
                    name=details.get('name', details.get('description', indicator_id)),
                    value=details['value'],
                    unit=details.get('unit', ''),
                    date=date,
                    source=source,
                    category=details.get('category', 'general'),
                    metadata_id=metadata.id if metadata else None
                )
                db.session.add(indicator)
                
                # Mettre à jour la date de dernière mise à jour des métadonnées
                if metadata:
                    metadata.last_updated = datetime.utcnow()
        
        db.session.commit()
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire pour la sérialisation JSON.
        
        Returns:
            dict: Représentation dictionnaire de l'indicateur économique.
        """
        return {
            'id': self.indicator_id,
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'date': self.date.isoformat(),
            'source': self.source,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': {
                'description': self.metadata_ref.description if self.metadata_ref else None,
                'frequency': self.metadata_ref.frequency if self.metadata_ref else None,
                'last_updated': self.metadata_ref.last_updated.isoformat() 
                    if self.metadata_ref and self.metadata_ref.last_updated else None
            } if self.metadata_ref or self.metadata_id else None
        }
        
    @classmethod
    def get_latest_indicators(cls, limit=10, include_metadata=False):
        """Récupère les derniers indicateurs économiques par date.
        
        Args:
            limit (int, optional): Nombre maximum d'indicateurs à retourner. Par défaut 10.
            include_metadata (bool, optional): Inclure les métadonnées associées. Par défaut False.
            
        Returns:
            list[EconomicIndicator]: Liste des indicateurs triés par date décroissante.
        """
        query = cls.query.options(
            db.joinedload(cls.metadata_ref)
        ).order_by(cls.date.desc(), cls.indicator_id).limit(limit)
        
        if include_metadata:
            return query.all()
        return query.options(db.load_only(
            'id', 'indicator_id', 'name', 'value', 'unit', 'date', 'source', 'category'
        )).all()
    
    @classmethod
    def get_indicators_by_category(cls, category, limit=10, include_metadata=False):
        """Récupère les derniers indicateurs d'une catégorie spécifique.
        
        Args:
            category (str): Catégorie des indicateurs à récupérer.
            limit (int, optional): Nombre maximum d'indicateurs à retourner. Par défaut 10.
            include_metadata (bool, optional): Inclure les métadonnées associées. Par défaut False.
            
        Returns:
            list[EconomicIndicator]: Liste des indicateurs de la catégorie triés par date décroissante.
        """
        query = cls.query.filter_by(category=category).options(
            db.joinedload(cls.metadata_ref)
        ).order_by(cls.date.desc(), cls.indicator_id).limit(limit)
        
        if include_metadata:
            return query.all()
        return query.options(db.load_only(
            'id', 'indicator_id', 'name', 'value', 'unit', 'date', 'source', 'category'
        )).all()
    
    @classmethod
    def get_indicator_history(cls, indicator_id, days=365, include_metadata=False):
        """Récupère l'historique d'un indicateur spécifique.
        
        Args:
            indicator_id (str): ID de l'indicateur.
            days (int, optional): Nombre de jours d'historique à récupérer. Par défaut 365.
            include_metadata (bool, optional): Inclure les métadonnées associées. Par défaut False.
            
        Returns:
            list[EconomicIndicator]: Liste des valeurs historiques de l'indicateur.
        """
        from datetime import datetime, timedelta
        
        date_limit = datetime.utcnow() - timedelta(days=days)
        query = cls.query.filter(
            cls.indicator_id == indicator_id,
            cls.date >= date_limit
        ).options(
            db.joinedload(cls.metadata_ref)
        ).order_by(cls.date.asc())
        
        if include_metadata:
            return query.all()
        return query.options(db.load_only(
            'id', 'indicator_id', 'name', 'value', 'unit', 'date', 'source', 'category'
        )).all()
    
    @classmethod
    def get_indicator_metadata(cls, indicator_id):
        """Récupère les métadonnées d'un indicateur spécifique.
        
        Args:
            indicator_id (str): ID de l'indicateur.
            
        Returns:
            IndicatorMetadata: Les métadonnées de l'indicateur, ou None si non trouvé.
        """
        return IndicatorMetadata.query.filter_by(indicator_id=indicator_id).first()
    
    @classmethod
    def get_available_categories(cls):
        """Récupère la liste des catégories d'indicateurs disponibles.
        
        Returns:
            list[str]: Liste des catégories uniques, triées par ordre alphabétique.
        """
        categories = db.session.query(
            cls.category.distinct().label('category')
        ).filter(cls.category.isnot(None)).order_by('category').all()
        return [c.category for c in categories]