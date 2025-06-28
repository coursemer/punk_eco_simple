# Punk Eco - Moroccan Economic Dashboard

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Web application for tracking and analyzing Moroccan economic indicators, providing an overview of the national economy through interactive dashboards and detailed analyses.

## 🌟 Features

- **Interactive dashboard** with key economic indicators
- **User authentication** with role-based access (admin/user)
- **RESTful API** for economic data access
- **Advanced data visualizations** with Plotly/Dash
- **Data export** in CSV, Excel, and JSON formats
- **Advanced search** and filtering of indicators
- **Alerts** for significant indicator variations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (recommended) or SQLite
- Node.js and npm (for frontend assets)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/coursemer/punk_eco_simple.git
   cd punk_eco_simple
   ```

2. **Set up the environment**
   ```bash
   # Create and activate a virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # .\venv\Scripts\activate  # Windows
   
   # Install dependencies
   pip install -e ".[dev]"
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit the .env file according to your configuration
   ```

4. **Initialize the database**
   ```bash
   flask db upgrade
   flask create-admin admin@example.com password
   ```

5. **Run the application**
   ```bash
   # Development mode
   flask run --debug
   
   # Or in production with Gunicorn
   gunicorn --bind 0.0.0.0:5000 wsgi:app
   ```

The application will be available at: http://localhost:5000

## Getting Started with Docker (Recommended)

1. **Create a .env file**
   ```bash
   cp .env.example .env
   ```

2. **Start the containers**
   ```bash
   docker-compose up -d
   ```

3. **Initialize the database**
   ```bash
   docker-compose exec web flask db upgrade
   docker-compose exec web flask create-admin admin@example.com password
   ```

The application will be available at: http://localhost:5000

## Useful Commands

### Development

```bash
# Format code
make format

# Run tests
make test

# Run tests with coverage
make test-cov

# Check code quality
make lint

# Clean temporary files
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
