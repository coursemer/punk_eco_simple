#!/bin/bash

# Punk Eco - Script de sauvegarde
# Ce script permet de sauvegarder la base de données et les fichiers média

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

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/backups/punk_eco"
DB_BACKUP_DIR="${BACKUP_DIR}/db"
MEDIA_BACKUP_DIR="${BACKUP_DIR}/media"
LOG_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.log"
KEEP_DAYS=30  # Nombre de jours de conservation des sauvegardes

# Créer les répertoires de sauvegarde s'ils n'existent pas
mkdir -p "${DB_BACKUP_DIR}" "${MEDIA_BACKUP_DIR}"

# Fonction pour journaliser les messages
log() {
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$message" | tee -a "${LOG_FILE}"
}

# Fonction pour sauvegarder la base de données
backup_database() {
    local backup_file="${DB_BACKUP_DIR}/db_${TIMESTAMP}.sql"
    
    log "Début de la sauvegarde de la base de données..."
    
    # Exporter la base de données PostgreSQL
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db pg_dump -U ${DB_USER} -d ${DB_NAME} > "${backup_file}"
    
    if [ $? -eq 0 ] && [ -s "${backup_file}" ]; then
        # Compresser le fichier de sauvegarde
        gzip -f "${backup_file}"
        log "Sauvegarde de la base de données terminée: ${backup_file}.gz"
        
        # Vérifier l'intégrité de la sauvegarde
        if gzip -t "${backup_file}.gz" 2>/dev/null; then
            log "Vérification de l'intégrité de la sauvegarde réussie"
        else
            log "ATTENTION: La sauvegarde semble corrompue"
        fi
    else
        log "ERREUR: Échec de la sauvegarde de la base de données"
        return 1
    fi
}

# Fonction pour sauvegarder les fichiers média
backup_media() {
    local backup_file="${MEDIA_BACKUP_DIR}/media_${TIMESTAMP}.tar.gz"
    
    log "Début de la sauvegarde des fichiers média..."
    
    # Créer une archive des fichiers média
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T web tar -czf - -C /app/instance/media . | cat > "${backup_file}"
    
    if [ $? -eq 0 ] && [ -s "${backup_file}" ]; then
        log "Sauvegarde des fichiers média terminée: ${backup_file}"
        
        # Vérifier l'intégrité de l'archive
        if gzip -t "${backup_file}" 2>/dev/null; then
            log "Vérification de l'intégrité de l'archive média réussie"
        else
            log "ATTENTION: L'archive média semble corrompue"
        fi
    else
        log "ERREUR: Échec de la sauvegarde des fichiers média"
        return 1
    fi
}

# Fonction pour nettoyer les anciennes sauvegardes
cleanup_old_backups() {
    log "Nettoyage des sauvegardes de plus de ${KEEP_DAYS} jours..."
    
    # Nettoyer les sauvegardes de base de données
    find "${DB_BACKUP_DIR}" -name "*.sql.gz" -mtime +${KEEP_DAYS} -delete 2>/dev/null
    
    # Nettoyer les sauvegardes de fichiers média
    find "${MEDIA_BACKUP_DIR}" -name "*.tar.gz" -mtime +${KEEP_DAYS} -delete 2>/dev/null
    
    # Nettoyer les anciens fichiers de log
    find "${BACKUP_DIR}" -name "*.log" -mtime +${KEEP_DAYS} -delete 2>/dev/null
    
    log "Nettoyage des anciennes sauvegardes terminé"
}

# Fonction pour calculer la taille d'un répertoire
get_directory_size() {
    local dir="$1"
    du -sh "${dir}" | cut -f1
}

# Fonction pour afficher l'aide
show_help() {
    echo "Utilisation: $0 [options]"
    echo "Options disponibles:"
    echo "  --db-only       Sauvegarder uniquement la base de données"
    echo "  --media-only    Sauvegarder uniquement les fichiers média"
    echo "  --no-cleanup    Ne pas nettoyer les anciennes sauvegardes"
    echo "  --help          Afficher cette aide"
    echo ""
    echo "Exemple: $0 --db-only --no-cleanup"
}

# Variables pour les options
BACKUP_DB=true
BACKUP_MEDIA=true
DO_CLEANUP=true

# Traiter les arguments de la ligne de commande
while [[ $# -gt 0 ]]; do
    case "$1" in
        --db-only)
            BACKUP_MEDIA=false
            shift
            ;;
        --media-only)
            BACKUP_DB=false
            shift
            ;;
        --no-cleanup)
            DO_CLEANUP=false
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

# Début du processus de sauvegarde
echo -e "\n${YELLOW}=== Début de la sauvegarde de Punk Eco ===${NC}"
echo -e "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "Répertoire de sauvegarde: ${BACKUP_DIR}"
echo -e "Conservation: ${KEEP_DAYS} jours\n"

# Journalisation
log "=== Démarrage de la sauvegarde ==="
log "Sauvegarde de la base de données: $([ "$BACKUP_DB" = true ] && echo "Oui" || echo "Non")"
log "Sauvegarde des fichiers média: $([ "$BACKUP_MEDIA" = true ] && echo "Oui" || echo "Non")"
log "Nettoyage des anciennes sauvegardes: $([ "$DO_CLEANUP" = true ] && echo "Oui" || echo "Non")"

# Sauvegarder la base de données si demandé
if [ "$BACKUP_DB" = true ]; then
    backup_database || {
        log "ERREUR: La sauvegarde de la base de données a échoué"
        exit 1
    }
fi

# Sauvegarder les fichiers média si demandé
if [ "$BACKUP_MEDIA" = true ]; then
    backup_media || {
        log "ERREUR: La sauvegarde des fichiers média a échoué"
        exit 1
    }
fi

# Nettoyer les anciennes sauvegardes si demandé
if [ "$DO_CLEANUP" = true ]; then
    cleanup_old_backups
fi

# Afficher un résumé
log "\n=== Résumé de la sauvegarde ==="
log "Date: $(date '+%Y-%m-%d %H:%M:%S')"

if [ "$BACKUP_DB" = true ]; then
    log "Dernière sauvegarde de la base de données: $(ls -t ${DB_BACKUP_DIR}/*.sql.gz 2>/dev/null | head -1 || echo "Aucune")"
    log "Taille du répertoire des sauvegardes BD: $(get_directory_size "${DB_BACKUP_DIR}")"
fi

if [ "$BACKUP_MEDIA" = true ]; then
    log "Dernière sauvegarde des fichiers média: $(ls -t ${MEDIA_BACKUP_DIR}/*.tar.gz 2>/dev/null | head -1 || echo "Aucune")"
    log "Taille du répertoire des sauvegardes média: $(get_directory_size "${MEDIA_BACKUP_DIR}")"
fi

log "Journal de la sauvegarde: ${LOG_FILE}"
log "=== Sauvegarde terminée avec succès ===\n"

echo -e "\n${GREEN}=== Sauvegarde terminée avec succès ===${NC}"
echo -e "Consultez le journal pour plus de détails: ${LOG_FILE}\n"

exit 0
