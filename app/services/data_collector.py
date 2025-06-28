"""
Service de collecte de données pour Punk Eco.
Combine les appels API et le web scraping pour collecter des données.
"""
import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime, timedelta
import os
import random
from typing import Dict, List, Any, Optional, Union

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockResponse:
    """Classe pour simuler les réponses HTTP"""
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data) if isinstance(json_data, dict) else str(json_data)
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            raise requests.exceptions.HTTPError(f"HTTP Error {self.status_code}")
        return None

class DataCollector:
    """Classe principale pour la collecte de données."""
    
    def __init__(self, db_session=None, simulation_mode=False, config=None):
        """Initialise le collecteur de données.
        
        Args:
            db_session: Session SQLAlchemy pour la base de données
            simulation_mode: Si True, utilise des données simulées au lieu d'appels API réels
            config: Dictionnaire de configuration (optionnel)
        """
        self.db_session = db_session
        self.simulation_mode = simulation_mode
        self.config = config or {}
        
        if not simulation_mode:
            self.session = requests.Session()
            # Configuration des en-têtes par défaut
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/html, application/xhtml+xml, application/xml;q=0.9, image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            })
        else:
            self.session = None
            logger.info("Mode simulation activé - utilisation de données simulées")
    
    def _make_api_call(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[Dict]:
        """Effectue un appel API et gère les erreurs."""
        if self.simulation_mode:
            logger.info(f"[SIMULATION] Appel API simulé: {url}")
            # Simulation d'une réponse d'API pour différents types de requêtes
            if 'electricitymap' in url:
                return self._simulate_electricity_map()
            elif 'api.emploi-store.fr' in url:
                return self._simulate_emploi_store()
            else:
                return {"status": "success", "data": [{"simulated": True, "url": url}]}
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de l'appel à l'API {url}: {e}")
            return None
    
    def scrape_website(self, url: str, selectors: Dict[str, str]) -> Dict:
        """
        Récupère le contenu d'une page web et extrait les données en utilisant des sélecteurs CSS.
        
        Args:
            url: URL de la page à scraper
            selectors: Dictionnaire de sélecteurs CSS pour extraire les données
            
        Returns:
            Dict contenant les données extraites
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            result = {}
            for key, selector in selectors.items():
                elements = soup.select(selector)
                if elements:
                    if len(elements) == 1:
                        result[key] = elements[0].get_text(strip=True)
                    else:
                        result[key] = [el.get_text(strip=True) for el in elements]
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors du scraping de {url}: {e}")
            return {}
    
    def collect_energy_data(self, source: str, **kwargs) -> Dict:
        """Collecte les données énergétiques depuis différentes sources."""
        if source == 'electricity_map':
            return self._collect_from_electricity_map(**kwargs)
        elif source == 'eia':
            return self._collect_from_eia(**kwargs)
        else:
            logger.warning(f"Source d'énergie non prise en charge: {source}")
            return {}
    
    def collect_economic_data(self, indicator_id: str, **kwargs) -> Dict:
        """Collecte des indicateurs économiques."""
        if indicator_id == 'inflation':
            return self._collect_inflation_data(**kwargs)
        elif indicator_id == 'unemployment':
            return self._collect_unemployment_data(**kwargs)
        else:
            logger.warning(f"Indicateur économique non pris en charge: {indicator_id}")
            return {}
    
    # Méthodes spécifiques aux sources de données
    
    def _collect_from_electricity_map(self, zone: str = 'FR') -> Dict:
        """Collecte les données de production d'électricité depuis Electricity Map."""
        url = f"https://api.electricitymap.org/v3/power-breakdown/latest"
        params = {
            'zone': zone,
        }
        headers = {
            'auth-token': self.config.get('ELECTRICITY_MAP_API_KEY', '')
        }
        return self._make_api_call(url, params=params, headers=headers)
    
    def _collect_from_eia(self, series_id: str) -> Dict:
        """Collecte des données depuis l'API de l'EIA (US Energy Information Administration)."""
        url = "https://api.eia.gov/v2/electricity/rto/daily-fuel-type-data/data/"
        params = {
            'api_key': self.config.get('EIA_API_KEY', ''),
            'frequency': 'daily',
            'data[0]': 'value',
            'facets[type][]': series_id,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': 1
        }
        return self._make_api_call(url, params=params)
    
    def _collect_inflation_data(self, country: str = 'france') -> List[Dict]:
        """Collecte les données d'inflation."""
        if self.simulation_mode:
            # Génération de données simulées pour l'inflation
            today = datetime.now()
            data_points = []
            
            # Génération de données pour les 12 derniers mois
            for i in range(12):
                date = (today - timedelta(days=30*i)).strftime("%Y-%m-%d")
                # Variation mensuelle simulée autour de 0.1% à 0.3%
                value = round(2.0 + random.uniform(-0.2, 0.5) + (i * 0.1), 1)
                data_points.append({
                    'date': date,
                    'value': value,
                    'country': country,
                    'source': 'simulation',
                    'indicator': 'inflation',
                    'unit': '%',
                    'frequency': 'monthly'
                })
            
            return data_points
        
        # Code original pour le scraping de l'INSEE
        url = "https://www.insee.fr/fr/statistiques/serie/010599691"
        
        # Scraping de la page
        soup = self.scrape_website(url, {
            'title': 'h1.titre',
            'last_update': '.mise-a-jour',
            'values': '.donnees-ligne .valeur',
            'dates': '.donnees-ligne .periode',
        })
        if not soup:
            return []
        
        try:
            # Exemple de sélecteur (à adapter selon la structure réelle de la page)
            data_points = []
            for row in soup.select('.tableau-nicerow'):
                date_elem = row.select_one('.date')
                value_elem = row.select_one('.valeur')
                
                if date_elem and value_elem:
                    data_points.append({
                        'date': date_elem.text.strip(),
                        'value': float(value_elem.text.strip().replace(',', '.')),
                        'country': country,
                        'source': 'insee',
                        'indicator': 'inflation',
                        'unit': '%',
                        'frequency': 'monthly'
                    })
            
            return data_points
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données d'inflation: {e}")
            return []
            selectors = {
                'title': 'h1.titre',
                'last_update': '.mise-a-jour',
                'values': '.donnees-ligne .valeur',
                'dates': '.donnees-ligne .periode',
            }
            return self.scrape_website(url, selectors)
        return {}
    
    def _collect_unemployment_data(self, country: str = 'france') -> List[Dict]:
        """Collecte les données de chômage."""
        if self.simulation_mode:
            # Génération de données simulées pour le chômage
            today = datetime.now()
            data_points = []
            
            # Génération de données pour les 12 derniers mois
            for i in range(12):
                date = (today - timedelta(days=30*i)).strftime("%Y-%m-%d")
                # Taux de chômage simulé entre 7% et 9%
                value = round(8.0 + random.uniform(-0.5, 0.5) + (i * 0.05), 1)
                data_points.append({
                    'date': date,
                    'value': value,
                    'country': country,
                    'source': 'simulation',
                    'indicator': 'unemployment_rate',
                    'unit': '%',
                    'frequency': 'monthly'
                })
            
            return data_points
            
        if country.lower() == 'france':
            # Exemple d'API pour les données de chômage
            url = "https://api.emploi-store.fr/partenaire/indicateur-mensuel/v1/indicateurs"
            
            # Paramètres de la requête
            params = {
                'codeZoneGeographique': 'FRANCE',
                'codeIndicateur': 'T3',  # Taux de chômage au sens du BIT
                'dateDebut': '2010-01-01',
                'dateFin': datetime.now().strftime('%Y-%m-%d')
            }
            
            # Récupération du token depuis la config ou les variables d'environnement
            token = self.config.get('EMPLOI_STORE_TOKEN') or os.getenv('EMPLOI_STORE_TOKEN')
            
            if not token:
                logger.error("Token d'authentification pour l'API emploi-store manquant")
                return []
            
            # En-têtes avec le token d'authentification
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            # Appel API
            data = self._make_api_call(url, params=params, headers=headers)
            
            if not data or not isinstance(data, list):
                return []
                
            # Traitement des données (à adapter selon la structure de la réponse)
            results = []
            for item in data:
                if 'date' in item and 'valeur' in item:
                    results.append({
                        'date': item['date'],
                        'value': item['valeur'],
                        'unit': '%',
                        'country': country,
                        'indicator': 'unemployment_rate',
                        'source': 'emploi_store',
                        'frequency': 'monthly'
                    })
                    
            return results
            
        return []

# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration avec des clés API (à stocker dans des variables d'environnement en production)
    config = {
        'ELECTRICITY_MAP_API_KEY': 'your_api_key_here',
        'EIA_API_KEY': 'your_eia_api_key_here',
        'EMPLOI_STORE_TOKEN': 'your_emploi_store_token_here'
    }
    
    collector = DataCollector(config)
    
    # Exemple de collecte de données énergétiques
    energy_data = collector.collect_energy_data('electricity_map', zone='FR')
    print("Données énergétiques:", energy_data)
    
    # Exemple de collecte de données économiques
    inflation_data = collector.collect_economic_data('inflation', country='france')
    print("\nDonnées d'inflation:", inflation_data)
