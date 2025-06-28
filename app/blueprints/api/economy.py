"""Routes API pour les données économiques."""

from flask import jsonify
from flask_jwt_extended import jwt_required
from app.models.ma_economy import EconomicIndicator
from . import api_bp

@api_bp.route('/economy/indicators', methods=['GET'])
@jwt_required()
def get_indicators():
    """Récupère les derniers indicateurs économiques."""
    indicators = EconomicIndicator.get_latest_indicators(limit=20)
    return jsonify({
        'status': 'success',
        'data': [indicator.to_dict() for indicator in indicators]
    }), 200

@api_bp.route('/economy/indicators/<string:indicator_id>', methods=['GET'])
@jwt_required()
def get_indicator_history(indicator_id):
    """Récupère l'historique d'un indicateur spécifique."""
    history = EconomicIndicator.get_indicator_history(indicator_id)
    return jsonify({
        'status': 'success',
        'data': [{
            'date': item.date.isoformat(),
            'value': item.value,
            'unit': item.unit
        } for item in history]
    }), 200

@api_bp.route('/economy/categories/<string:category>', methods=['GET'])
@jwt_required()
def get_indicators_by_category(category):
    """Récupère les indicateurs d'une catégorie spécifique."""
    indicators = EconomicIndicator.get_indicators_by_category(category)
    return jsonify({
        'status': 'success',
        'data': [indicator.to_dict() for indicator in indicators]
    }), 200
