#!/bin/bash

# Punk Eco - Script de déploiement
# Ce script permet de déployer l'application en production

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher un message d'information
info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Fonction pour afficher un message de succès
success() {
    echo -e "${GREEN}[SUCCÈS]${NC} $1"
}

# Fonction pour afficher un message d'erreur et quitter
error() {
    echo -e "${RED}[ERREUR]${NC} $1"
    exit 1
}

# Vérifier que le script est exécuté en tant que root
if [ "$(id -u)" -ne 0 ]; then
    error "Ce script doit être exécuté en tant que root"
fi

# Vérifier que docker et docker-compose sont installés
if ! command -v docker &> /dev/null; then
    error "Docker n'est pas installé. Veuillez l'installer avant de continuer."
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose n'est pas installé. Veuillez l'installer avant de continuer."
fi

# Charger les variables d'environnement
if [ -f .env ]; then
    info "Chargement des variables d'environnement..."
    export $(grep -v '^#' .env | xargs)
else
    error "Le fichier .env n'existe pas. Veuillez le créer à partir de .env.example"
fi

# Fonction pour initialiser les secrets Docker
init_secrets() {
    info "Initialisation des secrets Docker..."
    
    # Vérifier si les secrets existent déjà
    if ! docker secret inspect database_url &> /dev/null; then
        echo "postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}" | docker secret create database_url -
        success "Secret 'database_url' créé avec succès"
    else
        info "Le secret 'database_url' existe déjà"
    fi
    
    if ! docker secret inspect secret_key &> /dev/null; then
        echo "${SECRET_KEY}" | docker secret create secret_key -
        success "Secret 'secret_key' créé avec succès"
    else
        info "Le secret 'secret_key' existe déjà"
    fi
    
    if ! docker secret inspect mail_password &> /dev/null; then
        echo "${MAIL_PASSWORD}" | docker secret create mail_password -
        success "Secret 'mail_password' créé avec succès"
    else
        info "Le secret 'mail_password' existe déjà"
    fi
}

# Fonction pour arrêter et supprimer les conteneurs
stop_containers() {
    info "Arrêt des conteneurs en cours d'exécution..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
    success "Conteneurs arrêtés avec succès"
}

# Fonction pour démarrer les conteneurs en production
start_containers() {
    info "Démarrage des conteneurs en production..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
    
    # Vérifier que les conteneurs sont en cours d'exécution
    if [ $? -eq 0 ]; then
        success "Conteneurs démarrés avec succès"
    else
        error "Erreur lors du démarrage des conteneurs"
    fi
}

# Fonction pour effectuer les migrations de base de données
run_migrations() {
    info "Exécution des migrations de base de données..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T web flask db upgrade
    
    if [ $? -eq 0 ]; then
        success "Migrations exécutées avec succès"
    else
        error "Erreur lors de l'exécution des migrations"
    fi
}

# Fonction pour créer un superutilisateur
create_superuser() {
    info "Création d'un superutilisateur..."
    read -p "Email de l'administrateur: " ADMIN_EMAIL
    read -s -p "Mot de passe: " ADMIN_PASSWORD
    echo
    
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T web flask create-admin "$ADMIN_EMAIL" "$ADMIN_PASSWORD"
    
    if [ $? -eq 0 ]; then
        success "Superutilisateur créé avec succès"
    else
        error "Erreur lors de la création du superutilisateur"
    fi
}

# Fonction pour obtenir les certificats SSL
setup_ssl() {
    info "Configuration des certificats SSL avec Let's Encrypt..."
    
    # Arrêter temporairement nginx
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml stop nginx
    
    # Lancer certbot pour obtenir les certificats
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path /var/www/certbot/ -d ${DOMAIN} -d www.${DOMAIN}
    
    # Redémarrer nginx
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx
    
    success "Configuration SSL terminée"
}

# Fonction pour afficher l'aide
show_help() {
    echo "Utilisation: $0 [commande]"
    echo "Commandes disponibles:"
    echo "  init          Initialiser les secrets Docker"
    echo "  start         Démarrer les conteneurs en production"
    echo "  stop          Arrêter les conteneurs"
    echo "  restart       Redémarrer les conteneurs"
    echo "  migrate       Exécuter les migrations de base de données"
    echo "  createsuperuser Créer un superutilisateur"
    echo "  ssl           Configurer les certificats SSL"
    echo "  deploy        Déployer l'application (stop, build, start, migrate)"
    echo "  help          Afficher cette aide"
}

# Vérifier les arguments de la ligne de commande
case "$1" in
    init)
        init_secrets
        ;;
    start)
        start_containers
        ;;
    stop)
        stop_containers
        ;;
    restart)
        stop_containers
        start_containers
        ;;
    migrate)
        run_migrations
        ;;
    createsuperuser)
        create_superuser
        ;;
    ssl)
        setup_ssl
        ;;
    deploy)
        stop_containers
        start_containers
        run_migrations
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Commande non reconnue: $1${NC}"
        show_help
        exit 1
        ;;
esac

exit 0
