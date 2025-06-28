"""
Modèle pour stocker les résultats de la collecte de données.
"""
from ..extensions import db
from datetime import datetime
from sqlalchemy import JSON

class DataCollectionRun(db.Model):
    """Modèle pour suivre les exécutions de collecte de données."""
    __tablename__ = 'data_collection_runs'
    
    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(50), nullable=False)  # 'api' ou 'scraping'
    source_name = db.Column(db.String(100), nullable=False)  # Nom de la source (ex: 'electricity_map', 'insee')
    status = db.Column(db.String(20), default='started')  # 'started', 'completed', 'failed'
    parameters = db.Column(JSON)  # Paramètres de la requête
    result_count = db.Column(db.Integer, default=0)  # Nombre d'éléments collectés
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Relation avec les données collectées (one-to-many)
    collected_data = db.relationship('CollectedData', backref='run', lazy=True)
    
    def __repr__(self):
        return f'<DataCollectionRun {self.source_type}/{self.source_name} - {self.status}>'
    
    def mark_completed(self, count: int = 0):
        """Marque l'exécution comme terminée avec succès."""
        self.status = 'completed'
        self.result_count = count
        self.completed_at = datetime.utcnow()
    
    def mark_failed(self, error: str):
        """Marque l'exécution comme ayant échoué."""
        self.status = 'failed'
        self.error_message = str(error)[:1000]  # Limite la taille du message d'erreur
        self.completed_at = datetime.utcnow()


class CollectedData(db.Model):
    """Modèle pour stocker les données collectées."""
    __tablename__ = 'collected_data'
    
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('data_collection_runs.id'), nullable=False)
    data_type = db.Column(db.String(50), nullable=False)  # Type de données (ex: 'energy', 'inflation')
    source_id = db.Column(db.String(100), index=True)  # ID de la source d'origine
    collected_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    data_date = db.Column(db.DateTime, index=True)  # Date des données (peut être différente de collected_at)
    raw_data = db.Column(JSON)  # Données brutes
    processed = db.Column(db.Boolean, default=False)  # Indique si les données ont été traitées
    
    # Index pour les requêtes courantes
    __table_args__ = (
        db.Index('idx_collected_data_type_date', 'data_type', 'data_date'),
        db.Index('idx_collected_data_source', 'source_id', 'data_type'),
    )
    
    def __repr__(self):
        return f'<CollectedData {self.data_type} from {self.source_id} on {self.data_date}>'
    
    def to_dict(self):
        """Convertit les données en dictionnaire pour la sérialisation JSON."""
        return {
            'id': self.id,
            'run_id': self.run_id,
            'data_type': self.data_type,
            'source_id': self.source_id,
            'collected_at': self.collected_at.isoformat(),
            'data_date': self.data_date.isoformat() if self.data_date else None,
            'raw_data': self.raw_data,
            'processed': self.processed
        }
