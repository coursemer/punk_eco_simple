#!/usr/bin/env python3
"""
Script de test pour le système de collecte de données.
Permet de déclencher manuellement la collecte de données.
"""
import os
import sys
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services.data_collector import DataCollector
from app.tasks.data_collection_tasks import collect_energy_data, collect_economic_indicators

def main():
    """Fonction principale pour tester la collecte de données."""
    # Créer l'application Flask
    app = create_app('development')
    
    with app.app_context():
        logger.info("Début du test de collecte de données en mode simulation")
        
        # Créer une instance du collecteur en mode simulation
        collector = DataCollector(simulation_mode=True)
        
        # Tester la collecte de données énergétiques
        logger.info("Test de collecte des données énergétiques simulées...")
        try:
            energy_data = collector.collect_electricity_map_data()
            logger.info(f"Données énergétiques simulées collectées: {len(energy_data)} points de données")
            for i, data in enumerate(energy_data[:3]):  # Afficher les 3 premiers éléments
                logger.info(f"  Donnée {i+1}: {data}")
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des données énergétiques: {e}", exc_info=True)
        
        # Tester la collecte d'inflation
        logger.info("\nTest de collecte des données d'inflation simulées...")
        try:
            inflation_data = collector.collect_inflation_data()
            logger.info(f"Données d'inflation simulées collectées: {len(inflation_data)} points de données")
            for i, data in enumerate(inflation_data[:3]):  # Afficher les 3 premiers éléments
                logger.info(f"  Donnée {i+1}: {data}")
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des données d'inflation: {e}", exc_info=True)
        
        # Tester la collecte de données de chômage
        logger.info("\nTest de collecte des données de chômage simulées...")
        try:
            unemployment_data = collector.collect_unemployment_data()
            logger.info(f"Données de chômage simulées collectées: {len(unemployment_data)} points de données")
            for i, data in enumerate(unemployment_data[:3]):  # Afficher les 3 premiers éléments
                logger.info(f"  Donnée {i+1}: {data}")
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des données de chômage: {e}", exc_info=True)
            
        # Tester les tâches planifiées
        logger.info("\nTest des tâches planifiées...")
        try:
            # Tâche de collecte d'énergie
            logger.info("Exécution de la tâche de collecte d'énergie...")
            collect_energy_data()
            
            # Tâche de collecte d'indicateurs économiques
            logger.info("Exécution de la tâche de collecte d'indicateurs économiques...")
            collect_economic_indicators()
            
            logger.info("Toutes les tâches planifiées ont été exécutées avec succès en mode simulation")
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution des tâches planifiées: {e}", exc_info=True)
        
        logger.info("Test de collecte de données terminé")

if __name__ == "__main__":
    main()
