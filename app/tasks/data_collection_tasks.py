"""
Tâches planifiées pour la collecte automatique de données.
"""
import logging
from datetime import datetime, timedelta
from flask import current_app
from ..extensions import db
from ..models.data_collection import DataCollectionRun, CollectedData
from ..services.data_collector import DataCollector

# Configuration du logging
logger = logging.getLogger(__name__)

def collect_energy_data():
    """Tâche pour collecter les données énergétiques."""
    try:
        # Créer une entrée dans le journal des exécutions
        run = DataCollectionRun(
            source_type='api',
            source_name='electricity_map',
            status='started',
            parameters={
                'zone': 'FR',
                'data_type': 'energy_production'
            }
        )
        db.session.add(run)
        db.session.commit()
        
        # Initialiser le collecteur de données en mode simulation
        collector = DataCollector(
            config={
                'ELECTRICITY_MAP_API_KEY': current_app.config.get('ELECTRICITY_MAP_API_KEY', '')
            },
            simulation_mode=True
        )
        
        # Collecter les données
        energy_data = collector.collect_energy_data('electricity_map', zone='FR')
        
        if energy_data:
            # Enregistrer les données collectées
            collected_data = CollectedData(
                run_id=run.id,
                data_type='energy_production',
                source_id='electricity_map_FR',
                data_date=datetime.utcnow(),
                raw_data=energy_data
            )
            db.session.add(collected_data)
            run.mark_completed(count=1)
            logger.info(f"Données énergétiques collectées avec succès. Run ID: {run.id}")
        else:
            run.mark_failed("Aucune donnée retournée par l'API")
            logger.warning("Aucune donnée énergétique n'a été collectée")
        
    except Exception as e:
        db.session.rollback()
        if 'run' in locals():
            run.mark_failed(str(e))
        logger.error(f"Erreur lors de la collecte des données énergétiques: {e}", exc_info=True)
    finally:
        db.session.commit()

def collect_economic_indicators():
    """Tâche pour collecter les indicateurs économiques."""
    indicators = [
        ('inflation', 'france'),
        ('unemployment', 'france')
    ]
    
    for indicator_id, country in indicators:
        run = None
        try:
            # Créer une entrée dans le journal des exécutions
            run = DataCollectionRun(
                source_type='scraping' if indicator_id == 'inflation' else 'api',
                source_name=indicator_id,
                status='started',
                parameters={
                    'country': country,
                    'indicator': indicator_id
                }
            )
            db.session.add(run)
            db.session.commit()
            
            # Initialiser le collecteur de données en mode simulation
            collector = DataCollector(
                config={
                    'EMPLOI_STORE_TOKEN': current_app.config.get('EMPLOI_STORE_TOKEN', '')
                },
                simulation_mode=True
            )
            
            # Collecter les données
            data = collector.collect_economic_data(indicator_id, country=country)
            
            if data:
                # Enregistrer les données collectées
                collected_data = CollectedData(
                    run_id=run.id,
                    data_type=f'economic_{indicator_id}',
                    source_id=f'{indicator_id}_{country}',
                    data_date=datetime.utcnow(),
                    raw_data=data
                )
                db.session.add(collected_data)
                run.mark_completed(count=1)
                logger.info(f"Données économiques collectées pour {indicator_id}. Run ID: {run.id}")
            else:
                run.mark_failed("Aucune donnée retournée")
                logger.warning(f"Aucune donnée économique n'a été collectée pour {indicator_id}")
            
        except Exception as e:
            db.session.rollback()
            if run:
                run.mark_failed(str(e))
            logger.error(f"Erreur lors de la collecte des indicateurs économiques: {e}", exc_info=True)
        finally:
            db.session.commit()

def cleanup_old_data(days_to_keep=30):
    """Nettoie les anciennes données de collecte."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Supprimer d'abord les données collectées
        deleted_data = CollectedData.query.filter(
            CollectedData.collected_at < cutoff_date
        ).delete(synchronize_session=False)
        
        # Puis les exécutions sans données
        deleted_runs = DataCollectionRun.query.filter(
            DataCollectionRun.completed_at < cutoff_date
        ).delete(synchronize_session=False)
        
        db.session.commit()
        logger.info(f"Nettoyage des données: {deleted_data} données et {deleted_runs} exécutions supprimées")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors du nettoyage des anciennes données: {e}", exc_info=True)
