# app/services/ma_data_collectors/__init__.py
"""
Collecteurs de données pour les indicateurs économiques marocains.

Ce module fournit des classes pour collecter des données économiques
auprès de différentes sources officielles marocaines comme le HCP et Bank Al-Maghrib.
"""

from .hcp_collector import HCPCollector
from .bam_collector import BAMCollector

__all__ = ['HCPCollector', 'BAMCollector']

# Dictionnaire des collecteurs disponibles
COLLECTORS = {
    'hcp': HCPCollector,
    'bam': BAMCollector
}

def get_collector(source):
    """
    Retourne une instance du collecteur pour la source spécifiée.
    
    Args:
        source (str): Source de données ('hcp' ou 'bam')
        
    Returns:
        BaseCollector: Une instance du collecteur demandé
        
    Raises:
        ValueError: Si la source n'est pas reconnue
    """
    collector_class = COLLECTORS.get(source.lower())
    if not collector_class:
        raise ValueError(f"Source de données non prise en charge: {source}")
    return collector_class()