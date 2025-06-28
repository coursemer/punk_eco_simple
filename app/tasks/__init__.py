"""
Initialisation des tâches planifiées.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from . import data_collection_tasks
from .ma_economic_tasks import init_scheduler as init_ma_economic_scheduler

# Configuration du logging
logger = logging.getLogger(__name__)

# Créer le planificateur
scheduler = BackgroundScheduler()

def init_scheduler(app):
    """Initialise le planificateur de tâches."""
    with app.app_context():
        try:
            # Planifier la collecte des données énergétiques toutes les heures
            scheduler.add_job(
                id='collect_energy_data',
                func=data_collection_tasks.collect_energy_data,
                trigger=IntervalTrigger(hours=1),
                max_instances=1,
                replace_existing=True
            )
            
            # Planifier la collecte des indicateurs économiques tous les jours à minuit
            scheduler.add_job(
                id='collect_economic_indicators',
                func=data_collection_tasks.collect_economic_indicators,
                trigger='cron',
                hour=0,
                minute=0,
                max_instances=1,
                replace_existing=True
            )
            
            # Planifier le nettoyage des anciennes données tous les dimanches à 1h du matin
            scheduler.add_job(
                id='cleanup_old_data',
                func=data_collection_tasks.cleanup_old_data,
                trigger='cron',
                day_of_week='sun',
                hour=1,
                minute=0,
                max_instances=1,
                replace_existing=True,
                kwargs={'days_to_keep': 30}
            )
            
            # Initialiser les tâches économiques marocaines
            init_ma_economic_scheduler(app)
            
            # Démarrer le planificateur
            if not scheduler.running:
                scheduler.start()
                logger.info("Planificateur de tâches démarré")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du planificateur: {e}")

def shutdown_scheduler():
    """Arrête le planificateur de tâches."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Planificateur de tâches arrêté")
