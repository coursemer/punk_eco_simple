#!/bin/bash

# Punk Eco - Script de mise à jour
# Ce script permet de mettre à jour l'application en production

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

# Vérifier que git est installé
if ! command -v git &> /dev/null; then
    error "Git n'est pas installé. Veuillez l'installer avant de continuer."
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

# Fonction pour sauvegarder la base de données
backup_database() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_dir="/var/backups/punk_eco"
    local backup_file="${backup_dir}/db_backup_${timestamp}.sql"
    
    info "Sauvegarde de la base de données..."
    
    # Créer le répertoire de sauvegarde s'il n'existe pas
    mkdir -p "${backup_dir}"
    
    # Exporter la base de données PostgreSQL
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db pg_dump -U ${DB_USER} -d ${DB_NAME} > "${backup_file}"
    
    if [ $? -eq 0 ]; then
        success "Sauvegarde de la base de données terminée: ${backup_file}"
    else
        error "Échec de la sauvegarde de la base de données"
    fi
}

# Fonction pour mettre à jour le code source
update_source_code() {
    info "Mise à jour du code source..."
    
    # Récupérer les dernières modifications
    git fetch origin
    
    # Vérifier s'il y a des modifications locales non commitées
    if ! git diff-index --quiet HEAD --; then
        error "Il y a des modifications locales non commitées. Veuillez les valider ou les supprimer avant de continuer."
    fi
    
    # Obtenir le nom de la branche actuelle
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    
    # Mettre à jour la branche actuelle
    git pull origin "${current_branch}"
    
    if [ $? -ne 0 ]; then
        error "Échec de la mise à jour du code source"
    fi
    
    success "Code source mis à jour avec succès"
}

# Fonction pour reconstruire les images Docker
rebuild_containers() {
    info "Reconstruction des conteneurs Docker..."
    
    # Reconstruire les images
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
    
    if [ $? -ne 0 ]; then
        error "Échec de la reconstruction des conteneurs"
    fi
    
    success "Conteneurs reconstruits avec succès"
}

# Fonction pour redémarrer les services
restart_services() {
    info "Redémarrage des services..."
    
    # Redémarrer les conteneurs
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --force-recreate
    
    if [ $? -ne 0 ]; then
        error "Échec du redémarrage des services"
    fi
    
    success "Services redémarrés avec succès"
}

# Fonction pour exécuter les migrations
run_migrations() {
    info "Exécution des migrations de base de données..."
    
    # Attendre que les services soient prêts
    sleep 10
    
    # Exécuter les migrations
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T web flask db upgrade
    
    if [ $? -ne 0 ]; then
        error "Échec de l'exécution des migrations"
    fi
    
    success "Migrations exécutées avec succès"
}

# Fonction pour nettoyer les ressources inutilisées
cleanup() {
    info "Nettoyage des ressources Docker inutilisées..."
    
    # Supprimer les conteneurs arrêtés
    docker container prune -f
    
    # Supprimer les images non utilisées
    docker image prune -f
    
    # Supprimer les volumes non utilisés
    docker volume prune -f
    
    # Supprimer les réseaux non utilisés
    docker network prune -f
    
    success "Nettoyage terminé"
}

# Fonction pour afficher l'aide
show_help() {
    echo "Utilisation: $0 [options]"
    echo "Options disponibles:"
    echo "  --backup       Effectuer une sauvegarde de la base de données avant la mise à jour"
    echo "  --no-backup    Ne pas effectuer de sauvegarde de la base de données"
    echo "  --migrate      Exécuter les migrations de base de données après la mise à jour"
    echo "  --no-migrate   Ne pas exécuter les migrations de base de données"
    echo "  --cleanup      Nettoyer les ressources Docker inutilisées après la mise à jour"
    echo "  --help         Afficher cette aide"
    echo ""
    echo "Exemple: $0 --backup --migrate --cleanup"
}

# Variables pour les options
DO_BACKUP=true
DO_MIGRATE=true
DO_CLEANUP=false

# Traiter les arguments de la ligne de commande
while [[ $# -gt 0 ]]; do
    case "$1" in
        --backup)
            DO_BACKUP=true
            shift
            ;;
        --no-backup)
            DO_BACKUP=false
            shift
            ;;
        --migrate)
            DO_MIGRATE=true
            shift
            ;;
        --no-migrate)
            DO_MIGRATE=false
            shift
            ;;
        --cleanup)
            DO_CLEANUP=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Option non reconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# Début du processus de mise à jour
echo -e "\n${YELLOW}=== Début de la mise à jour de Punk Eco ===${NC}\n"

# Effectuer une sauvegarde si demandé
if [ "$DO_BACKUP" = true ]; then
    backup_database
else
    info "Sauvegarde de la base de données ignorée (--no-backup)"
fi

# Mettre à jour le code source
update_source_code

# Reconstruire les conteneurs
rebuild_containers

# Redémarrer les services
restart_services

# Exécuter les migrations si demandé
if [ "$DO_MIGRATE" = true ]; then
    run_migrations
else
    info "Exécution des migrations ignorée (--no-migrate)"
fi

# Nettoyer les ressources inutilisées si demandé
if [ "$DO_CLEANUP" = true ]; then
    cleanup
fi

echo -e "\n${GREEN}=== Mise à jour terminée avec succès ! ===${NC}\n"

# Afficher les informations de déploiement
info "Vérification du statut des services..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

echo -e "\n${GREEN}L'application est maintenant à jour et en cours d'exécution.${NC}"
echo -e "${YELLOW}URL: https://${DOMAIN:-localhost}${NC}\n"

exit 0
