"""Energy-related models for the Punk Eco application."""
from ..extensions import db
from datetime import datetime

class EnergySource(db.Model):
    """Model representing an energy source."""
    __tablename__ = 'energy_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    source_type = db.Column(db.String(50), nullable=False)  # e.g., 'solar', 'wind', 'grid'
    capacity = db.Column(db.Float, nullable=True)  # in kW
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    energy_data = db.relationship('EnergyData', backref='source', lazy=True)

    def __repr__(self):
        return f'<EnergySource {self.name} ({self.source_type})>'


class EnergyData(db.Model):
    """Model for storing energy production/consumption data."""
    __tablename__ = 'energy_data'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('energy_sources.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    value = db.Column(db.Float, nullable=False)  # in kWh
    measurement_type = db.Column(db.String(50), nullable=False)  # e.g., 'production', 'consumption'
    
    def __repr__(self):
        return f'<EnergyData {self.measurement_type} {self.value}kWh at {self.timestamp}>'
