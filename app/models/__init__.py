"""
Modèles de données pour l'application Punk Eco.
"""
from .user import User

# Import des autres modèles
from .energy import EnergySource, EnergyData
from .trade import TradeData
from .data_collection import DataCollectionRun, CollectedData

# Import du modèle économique principal
from .ma_economy import EconomicIndicator, IndicatorMetadata

# Alias pour la rétrocompatibilité
LegacyEconomicIndicator = EconomicIndicator

# Initialisation des modèles
def init_app(app):
    """Initialise les modèles avec l'application Flask."""
    # Cette fonction peut être utilisée pour effectuer des opérations d'initialisation
    # Tous les modèles sont importés ci-dessus et enregistrés avec SQLAlchemy
    # spécifiques aux modèles si nécessaire
    pass

# Liste de tous les modèles pour faciliter l'import
def get_models():
    """Retourne un dictionnaire de tous les modèles."""
    return {
        'User': User,
        'EnergySource': EnergySource,
        'EnergyData': EnergyData,
        'EconomicIndicator': LegacyEconomicIndicator,  # Ancien modèle
        'MAEconomicIndicator': EconomicIndicator,  # Nouveau modèle pour les indicateurs économiques du Maroc
        'IndicatorMetadata': IndicatorMetadata,
        'TradeData': TradeData,
        'DataCollectionRun': DataCollectionRun,
        'CollectedData': CollectedData,
    }
