"""Trade data models for the Punk Eco application."""
from ..extensions import db
from datetime import datetime

class TradeData(db.Model):
    """Model representing trade data."""
    __tablename__ = 'trade_data'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    asset = db.Column(db.String(50), nullable=False)  # e.g., 'BTC', 'ETH', 'SOL'
    side = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    amount = db.Column(db.Float, nullable=False)  # Amount of the asset
    price = db.Column(db.Float, nullable=False)  # Price per unit in the base currency
    total = db.Column(db.Float, nullable=False)  # Total value (amount * price)
    fee = db.Column(db.Float, default=0.0)  # Transaction fee
    status = db.Column(db.String(20), default='completed')  # e.g., 'pending', 'completed', 'failed'
    exchange = db.Column(db.String(100))  # Exchange name if applicable
    notes = db.Column(db.Text)  # Any additional notes
    
    # Foreign key to user who made the trade (if applicable)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TradeData {self.side} {self.amount} {self.asset} @ {self.price} on {self.timestamp}>'
    
    def to_dict(self):
        """Convert trade data to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'asset': self.asset,
            'side': self.side,
            'amount': self.amount,
            'price': self.price,
            'total': self.total,
            'fee': self.fee,
            'status': self.status,
            'exchange': self.exchange,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
