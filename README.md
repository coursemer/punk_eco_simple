# Punk Eco - Tableau de Bord de l'Économie Marocaine

[![Licence MIT](https://img.shields.io/badge/Licence-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Application web de suivi et d'analyse des indicateurs économiques marocains, offrant une vue d'ensemble de l'économie nationale à travers des tableaux de bord interactifs et des analyses détaillées.

## 🌟 Fonctionnalités

- **Tableau de bord interactif** avec indicateurs économiques clés
- **Authentification** des utilisateurs avec rôles (admin/utilisateur)
- **API RESTful** pour l'accès aux données économiques
- **Visualisations** de données avancées avec Plotly/Dash
- **Export** des données aux formats CSV, Excel et JSON
- **Recherche** et filtrage avancé des indicateurs
- **Alertes** sur les variations importantes des indicateurs

## 🚀 Démarrage rapide

### Prérequis

- Python 3.8 ou supérieur
- PostgreSQL (recommandé) ou SQLite
- Node.js et npm (pour les assets frontend)
- Git

### Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/punk-eco/moroccan-economy-dashboard.git
   cd moroccan-economy-dashboard
   ```

2. **Configurer l'environnement**
   ```bash
   # Créer et activer un environnement virtuel
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # .\venv\Scripts\activate  # Windows
   
   # Installer les dépendances
   pip install -e ".[dev]"
   ```

3. **Configurer les variables d'environnement**
   ```bash
   cp .env.example .env
   # Éditer le fichier .env selon votre configuration
   ```

4. **Initialiser la base de données**
   ```bash
   flask db upgrade
   flask create-admin admin@example.com motdepasse
   ```

5. **Lancer l'application**
   ```bash
   # Mode développement
   flask run --debug
   
   # Ou en production avec Gunicorn
   gunicorn --bind 0.0.0.0:5000 wsgi:app
   ```

L'application sera disponible à l'adresse : http://localhost:5000

## 🐳 Démarrage avec Docker (recommandé)

1. **Créer un fichier .env**
   ```bash
   cp .env.example .env
   ```

2. **Démarrer les conteneurs**
   ```bash
   docker-compose up -d
   ```

3. **Initialiser la base de données**
   ```bash
   docker-compose exec web flask db upgrade
   docker-compose exec web flask create-admin admin@example.com motdepasse
   ```

L'application sera disponible à l'adresse : http://localhost:5000

## 🛠 Commandes utiles

### Développement

```bash
# Formater le code
make format

# Lancer les tests
make test

# Lancer les tests avec couverture
make test-cov

# Vérifier la qualité du code
make lint

# Nettoyer les fichiers temporaires
make clean
```

### Production

```bash
# Déployer l'application en production
./deploy.sh

# Mettre à jour l'application
./update.sh

# Effectuer une sauvegarde
./backup.sh

# Vérifier l'état du système
./monitoring.sh

# Configurer un nouveau serveur (nécessite des droits root)
sudo ./setup_server.sh
```

## 📂 Structure du projet

```
punk_eco/
├── app/                      # Package principal
│   ├── __init__.py           # Initialisation et factory
│   ├── app.py                # Configuration de l'application
│   ├── cli.py                # Commandes personnalisées
│   ├── models/               # Modèles de données
│   │   ├── __init__.py
│   │   └── user.py           # Modèle utilisateur
│   ├── auth/                 # Authentification
│   │   ├── __init__.py
│   │   └── routes.py         # Routes d'authentification
│   ├── api/                  # Points d'API REST
│   │   ├── __init__.py
│   │   └── v1/               # Version 1 de l'API
│   ├── static/               # Fichiers statiques
│   │   ├── css/              # Feuilles de style
│   │   ├── js/               # Scripts JavaScript
│   │   └── img/              # Images
│   └── templates/            # Templates Jinja2
│       ├── base.html         # Template de base
│       └── auth/             # Templates d'authentification
├── tests/                    # Tests automatisés
├── migrations/               # Migrations de base de données
├── instance/                 # Fichiers d'instance
├── nginx/                    # Configuration Nginx
│   ├── nginx.conf           # Configuration principale
│   └── conf.d/              # Configuration des sites
│       └── punk_eco.conf    # Configuration du site Punk Eco
├── .github/                  # Configuration GitHub
├── .docker/                  # Fichiers de configuration Docker
├── .env.example             # Exemple de configuration
├── .gitignore
├── .pre-commit-config.yaml   # Configuration pre-commit
├── docker-compose.yml        # Configuration Docker Compose de base
├── docker-compose.override.yml # Surcharges pour le développement
├── docker-compose.prod.yml   # Configuration Docker Compose pour la production
├── Dockerfile               # Configuration Docker
├── MANIFEST.in              # Fichiers à inclure dans le package
├── pytest.ini               # Configuration pytest
├── requirements.txt         # Dépendances principales
├── requirements-dev.txt     # Dépendances de développement
├── setup.py                 # Configuration du package
├── .dockerignore            # Fichiers à ignorer par Docker
├── punk_eco_crontab         # Tâches planifiées
├── deploy.sh                # Script de déploiement
├── update.sh                # Script de mise à jour
├── backup.sh                # Script de sauvegarde
├── monitoring.sh            # Script de surveillance
├── setup_server.sh          # Script de configuration du serveur
├── INSTALL.md               # Guide d'installation détaillé
├── UPGRADE.md               # Guide de mise à jour
├── MAINTENANCE.md           # Guide de maintenance
└── README.md               # Ce fichier
```

## 🧪 Tests

Les tests utilisent pytest et peuvent être exécutés avec :

```bash
# Tous les tests
pytest

# Un fichier spécifique
pytest tests/test_auth.py

# Avec couverture de code
pytest --cov=app

# Générer un rapport HTML de couverture
pytest --cov=app --cov-report=html
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. **Signaler un bug**
   - Vérifiez s'il n'existe pas déjà une issue ouverte
   - Ouvrez une nouvelle issue avec une description claire

2. **Proposer une amélioration**
   - Créez une branche pour votre fonctionnalité
   - Implémentez vos modifications
   - Ajoutez des tests pertinents
   - Soumettez une pull request

## 📚 Documentation complète

Pour plus de détails sur l'installation, la configuration et la maintenance, consultez :

- [Guide d'installation](INSTALL.md) - Instructions détaillées pour installer et configurer l'application
- [Guide de mise à jour](UPGRADE.md) - Procédures pour mettre à jour l'application vers de nouvelles versions
- [Guide de maintenance](MAINTENANCE.md) - Tâches de maintenance courantes et dépannage
- [Code de conduite](CODE_OF_CONDUCT.md) - Normes de comportement pour la communauté
- [Politique de sécurité](SECURITY.md) - Politique de signalement des vulnérabilités
- [Journal des modifications](CHANGELOG.md) - Historique des changements par version

## 🔒 Sécurité

Pour signaler une vulnérabilité de sécurité, veuillez consulter notre [politique de sécurité](SECURITY.md).

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez lire notre [guide de contribution](CONTRIBUTING.md) pour commencer.

## 📝 Licence

Ce projet est sous licence [MIT](LICENSE).

## 📞 Contact

Pour toute question ou suggestion, n'hésitez pas à nous contacter à [contact@punk-eco.ma](mailto:contact@punk-eco.ma).

---

<div align="center">
  <p>Développé avec ❤️ par l'équipe <strong>Punk Eco</strong></p>
  <p>
    <a href="https://punk-eco.ma">Site Web</a> • 
    <a href="https://twitter.com/punkeco">Twitter</a> • 
    <a href="https://github.com/punk-eco">GitHub</a>
  </p>
</div>
