"""
Classe de base pour les collecteurs de données économiques marocaines.

Cette classe définit l'interface commune que tous les collecteurs doivent implémenter.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """Classe abstraite de base pour les collecteurs de données économiques."""
    
    def __init__(self, use_cache: bool = True):
        """Initialise le collecteur avec un cache optionnel.
        
        Args:
            use_cache: Si True, utilise le cache pour stocker les résultats
        """
        self.use_cache = use_cache
        self.cache = {}
    
    @abstractmethod
    def collect(self) -> Dict:
        """Collecte les données depuis la source.
        
        Returns:
            Un dictionnaire contenant les données collectées au format standardisé.
            
            Exemple de format de retour:
            {
                "date": "2023-01-01",
                "source": "HCP",
                "indicators": {
                    "indicator_id": {
                        "value": 123.45,
                        "unit": "%",
                        "description": "Description de l'indicateur",
                        "category": "category_name"
                    },
                    ...
                }
            }
        """
        pass
    
    def get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Récupère des données en cache si disponible et si le cache est activé.
        
        Args:
            cache_key: Clé pour accéder aux données en cache
            
        Returns:
            Les données en cache ou None si non trouvées ou si le cache est désactivé
        """
        if not self.use_cache:
            return None
            
        return self.cache.get(cache_key)
    
    def set_cached_data(self, cache_key: str, data: Dict) -> None:
        """Stocke des données dans le cache si le cache est activé.
        
        Args:
            cache_key: Clé pour stocker les données
            data: Données à mettre en cache
        """
        if not self.use_cache:
            return
            
        self.cache[cache_key] = data
    
    def clear_cache(self) -> None:
        """Vide le cache du collecteur."""
        self.cache.clear()
        
    def __str__(self) -> str:
        """Représentation en chaîne du collecteur."""
        return f"{self.__class__.__name__}(use_cache={self.use_cache})"
