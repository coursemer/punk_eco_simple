# Makefile pour Punk Eco - Commandes utiles pour le développement

# Variables
PYTHON = python
PIP = pip
FLAKE8 = flake8
BLACK = black
ISORT = isort
PYTEST = pytest
DOCKER = docker
DOCKER_COMPOSE = docker-compose

# Chemins
SRC = app
TESTS = tests

# Commandes par défaut
.DEFAULT_GOAL := help

# Afficher l'aide
dev: help

help:
	@echo "\nCommandes disponibles :"
	@echo "\nDéveloppement :"
	@echo "  make dev-install     Installer les dépendances de développement"
	@echo "  make format          Formater le code avec Black et isort"
	@echo "  make lint            Vérifier la qualité du code avec flake8 et black"
	@echo "  make test            Exécuter les tests unitaires"
	@echo "  make test-cov        Exécuter les tests avec couverture de code"
	@echo "  make clean           Nettoyer les fichiers temporaires"
	@echo "\nDocker :"
	@echo "  make docker-build    Construire les images Docker"
	@echo "  make docker-up       Démarrer les conteneurs en arrière-plan"
	@echo "  make docker-down     Arrêter les conteneurs"
	@echo "  make docker-logs     Afficher les logs des conteneurs"
	@echo "  make docker-bash     Ouvrir un shell dans le conteneur web"

# Installation
dev-install:
	$(PIP) install -e .
	$(PIP) install -r requirements-dev.txt

# Formatage du code
format:
	$(BLACK) $(SRC) $(TESTS) setup.py
	$(ISORT) $(SRC) $(TESTS) setup.py

# Vérification de la qualité du code
lint:
	$(FLAKE8) $(SRC) $(TESTS) setup.py
	$(BLACK) --check $(SRC) $(TESTS) setup.py

# Tests
test:
	$(PYTEST) -v $(TESTS)

test-cov:
	$(PYTEST) --cov=$(SRC) --cov-report=term-missing --cov-report=html $(TESTS)

# Nettoyage
clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete
	find . -type f -name '*~' -delete
	find . -type f -name '.coverage' -delete
	docker system prune -f

# Docker
docker-build:
	$(DOCKER_COMPOSE) build

docker-up:
	$(DOCKER_COMPOSE) up -d

docker-down:
	$(DOCKER_COMPOSE) down

docker-logs:
	$(DOCKER_COMPOSE) logs -f

docker-bash:
	$(DOCKER_COMPOSE) exec web bash

.PHONY: help dev-install format lint test test-cov clean docker-build docker-up docker-down docker-logs docker-bash
