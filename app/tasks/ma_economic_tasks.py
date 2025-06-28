from datetime import datetime, timedelta
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app import db
from app.models.ma_economy import EconomicIndicator
from app.services.ma_data_collectors.hcp_collector import HCPCollector
from app.services.ma_data_collectors.bam_collector import BAMCollector

def init_scheduler(app):
    """Initialise le planificateur de tâches."""
    scheduler = BackgroundScheduler(daemon=True)
    
    with app.app_context():
        # Planifier la collecte des données HCP (tous les jours à minuit)
        scheduler.add_job(
            collect_hcp_data,
            trigger=IntervalTrigger(days=1, start_date=datetime.now() + timedelta(seconds=10)),
            id='collect_hcp_data',
            name='Collecte des données HCP (PIB, inflation, chômage)',
            replace_existing=True
        )
        
        # Planifier la collecte des données BAM (tous les jours à 1h du matin)
        scheduler.add_job(
            collect_bam_data,
            trigger=IntervalTrigger(days=1, start_date=datetime.now() + timedelta(hours=1, seconds=10)),
            id='collect_bam_data',
            name='Collecte des données BAM (TMM)',
            replace_existing=True
        )
        
        # Démarrer le planificateur
        scheduler.start()
        logging.info("Planificateur de tâches démarré")

def collect_hcp_data():
    """Collecte les données du HCP (PIB, inflation, chômage)."""
    try:
        collector = HCPCollector()
        data = collector.collect()
        
        if data:
            EconomicIndicator.save_from_dict(data)
            logging.info("Données HCP collectées avec succès")
        else:
            logging.warning("Aucune donnée HCP n'a été collectée")
            
    except Exception as e:
        logging.error(f"Erreur lors de la collecte des données HCP: {str(e)}")
        db.session.rollback()

def collect_bam_data():
    """Collecte les données de la BAM (TMM)."""
    try:
        collector = BAMCollector()
        data = collector.collect()
        
        if data:
            EconomicIndicator.save_from_dict(data)
            logging.info("Données BAM collectées avec succès")
        else:
            logging.warning("Aucune donnée BAM n'a été collectée")
            
    except Exception as e:
        logging.error(f"Erreur lors de la collecte des données BAM: {str(e)}")
        db.session.rollback()

# Pour exécution manuelle si nécessaire
if __name__ == "__main__":
    from app import create_app
    
    app = create_app()
    with app.app_context():
        collect_hcp_data()
        collect_bam_data()
