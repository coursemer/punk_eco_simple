#!/bin/bash

# Punk Eco - Script de surveillance
# Ce script permet de surveiller l'état de l'application et des services

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LOG_DIR="/var/log/punk_eco"
LOG_FILE="${LOG_DIR}/monitoring_$(date +"%Y%m%d").log"
STATUS_FILE="/tmp/punk_eco_status.json"
ALERT_THRESHOLD=90  # Seuil d'alerte en pourcentage
EMAIL_TO="admin@punk-eco.ma"

# Fonction pour initialiser les répertoires de log
init_logs() {
    mkdir -p "${LOG_DIR}"
    touch "${LOG_FILE}"
}

# Fonction pour journaliser les messages
log() {
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$message" | tee -a "${LOG_FILE}"
}

# Fonction pour vérifier l'état des conteneurs Docker
check_containers() {
    log "Vérification des conteneurs Docker..."
    
    local output
    output=$(docker ps --format '{{.Names}}|{{.Status}}|{{.State}}' 2>&1)
    
    if [ $? -ne 0 ]; then
        log "${RED}ERREUR: Impossible de vérifier les conteneurs Docker${NC}"
        send_alert "Erreur Docker" "Impossible de vérifier les conteneurs Docker: $output"
        return 1
    fi
    
    local all_running=true
    
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            local container_name=$(echo "$line" | cut -d'|' -f1)
            local status=$(echo "$line" | cut -d'|' -f2)
            local state=$(echo "$line" | cut -d'|' -f3)
            
            if [ "$state" != "running" ]; then
                log "${RED}ALERTE: Le conteneur $container_name n'est pas en cours d'exécution (Statut: $status)${NC}"
                send_alert "Conteneur arrêté" "Le conteneur $container_name n'est pas en cours d'exécution (Statut: $status)"
                all_running=false
            else
                log "${GREEN}OK: Le conteneur $container_name est en cours d'exécution (Statut: $status)${NC}"
            fi
        fi
    done <<< "$output"
    
    if [ "$all_running" = true ]; then
        log "${GREEN}Tous les conteneurs sont en cours d'exécution${NC}"
    fi
}

# Fonction pour vérifier l'utilisation du disque
check_disk_usage() {
    log "Vérification de l'utilisation du disque..."
    
    local output
    output=$(df -h / | awk 'NR==2 {print $5 "|" $3 "|" $4 "|" $2}')
    
    if [ $? -ne 0 ]; then
        log "${RED}ERREUR: Impossible de vérifier l'utilisation du disque${NC}"
        return 1
    fi
    
    local usage_percent=$(echo "$output" | cut -d'%' -f1 | cut -d'|' -f1)
    local used=$(echo "$output" | cut -d'|' -f2)
    local available=$(echo "$output" | cut -d'|' -f3)
    local total=$(echo "$output" | cut -d'|' -f4)
    
    log "Utilisation du disque: $usage_percent% (Utilisé: $used, Disponible: $available, Total: $total)"
    
    if [ "${usage_percent%%.*}" -ge "$ALERT_THRESHOLD" ]; then
        local message="L'utilisation du disque est de $usage_percent% (Seuil: $ALERT_THRESHOLD%)"
        log "${RED}ALERTE: $message${NC}"
        send_alert "Utilisation élevée du disque" "$message\nUtilisé: $used\nDisponible: $available\nTotal: $total"
    fi
}

# Fonction pour vérifier l'utilisation de la mémoire
check_memory_usage() {
    log "Vérification de l'utilisation de la mémoire..."
    
    local output
    output=$(free -m | awk 'NR==2 {print $3 "|" $4 "|" $2}')
    
    if [ $? -ne 0 ]; then
        log "${RED}ERREUR: Impossible de vérifier l'utilisation de la mémoire${NC}"
        return 1
    fi
    
    local used_mb=$(echo "$output" | cut -d'|' -f1)
    local free_mb=$(echo "$output" | cut -d'|' -f2)
    local total_mb=$(echo "$output" | cut -d'|' -f3)
    
    local used_percent=$((used_mb * 100 / total_mb))
    
    log "Utilisation de la mémoire: $used_percent% (Utilisé: ${used_mb}M, Libre: ${free_mb}M, Total: ${total_mb}M)"
    
    if [ "$used_percent" -ge "$ALERT_THRESHOLD" ]; then
        local message="L'utilisation de la mémoire est de $used_percent% (Seuil: $ALERT_THRESHOLD%)"
        log "${RED}ALERTE: $message${NC}"
        send_alert "Utilisation élevée de la mémoire" "$message\nUtilisé: ${used_mb}M\nLibre: ${free_mb}M\nTotal: ${total_mb}M"
    fi
}

# Fonction pour vérifier l'utilisation du CPU
check_cpu_usage() {
    log "Vérification de l'utilisation du CPU..."
    
    local usage_percent
    usage_percent=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}' | cut -d'.' -f1)
    
    if [ $? -ne 0 ]; then
        log "${RED}ERREUR: Impossible de vérifier l'utilisation du CPU${NC}"
        return 1
    fi
    
    log "Utilisation du CPU: $usage_percent%"
    
    if [ "$usage_percent" -ge "$ALERT_THRESHOLD" ]; then
        local message="L'utilisation du CPU est de $usage_percent% (Seuil: $ALERT_THRESHOLD%)"
        log "${RED}ALERTE: $message${NC}"
        send_alert "Utilisation élevée du CPU" "$message"
    fi
}

# Fonction pour vérifier l'état de la base de données
check_database() {
    log "Vérification de la base de données..."
    
    # Vérifier si le conteneur de base de données est en cours d'exécution
    if ! docker ps | grep -q "db"; then
        log "${RED}ERREUR: Le conteneur de base de données n'est pas en cours d'exécution${NC}"
        send_alert "Base de données indisponible" "Le conteneur de base de données n'est pas en cours d'exécution"
        return 1
    fi
    
    # Vérifier la connexion à la base de données
    local output
    output=$(docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db pg_isready -U ${DB_USER} -d ${DB_NAME} 2>&1)
    
    if [[ "$output" == *"accepting connections"* ]]; then
        log "${GREEN}La base de données est accessible${NC}"
    else
        log "${RED}ERREUR: Impossible de se connecter à la base de données: $output${NC}"
        send_alert "Erreur de connexion à la base de données" "Impossible de se connecter à la base de données: $output"
        return 1
    fi
    
    # Vérifier les connexions actives
    local connections
    connections=$(docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db psql -U ${DB_USER} -d ${DB_NAME} -t -c "SELECT count(*) FROM pg_stat_activity;" 2>&1 | tr -d '[:space:]')
    
    if [ $? -eq 0 ] && [ -n "$connections" ] && [ "$connections" -gt 0 ]; then
        log "Connexions actives à la base de données: $connections"
    else
        log "${YELLOW}ATTENTION: Impossible de vérifier les connexions à la base de données${NC}"
    fi
}

# Fonction pour vérifier l'état de Redis
check_redis() {
    log "Vérification de Redis..."
    
    # Vérifier si le conteneur Redis est en cours d'exécution
    if ! docker ps | grep -q "redis"; then
        log "${RED}ERREUR: Le conteneur Redis n'est pas en cours d'exécution${NC}"
        send_alert "Redis indisponible" "Le conteneur Redis n'est pas en cours d'exécution"
        return 1
    fi
    
    # Vérifier la connexion à Redis
    local output
    output=$(docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T redis redis-cli ping 2>&1)
    
    if [ "$output" = "PONG" ]; then
        log "${GREEN}Redis est accessible${NC}"
    else
        log "${RED}ERREUR: Impossible de se connecter à Redis: $output${NC}"
        send_alert "Erreur de connexion à Redis" "Impossible de se connecter à Redis: $output"
        return 1
    fi
}

# Fonction pour vérifier l'état de l'application web
check_web_application() {
    log "Vérification de l'application web..."
    
    local url="http://localhost:5000/health"
    local status_code=0
    local response=""
    
    # Essayer de récupérer la page de santé
    if command -v curl &> /dev/null; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>&1)
        status_code=$?
    elif command -v wget &> /dev/null; then
        response=$(wget --spider -S "$url" 2>&1 | grep "HTTP/" | tail -1 | awk '{print $2}')
        status_code=$?
    else
        log "${YELLOW}ATTENTION: Ni curl ni wget n'est disponible pour vérifier l'application web${NC}"
        return 1
    fi
    
    if [ "$status_code" -eq 0 ] && [ "$response" = "200" ]; then
        log "${GREEN}L'application web est accessible (Code: $response)${NC}"
    else
        log "${RED}ERREUR: L'application web est inaccessible ou en erreur (Code: $response)${NC}"
        send_alert "Application web inaccessible" "L'application web est inaccessible ou en erreur (Code: $response)"
        return 1
    fi
}

# Fonction pour envoyer une alerte par email
send_alert() {
    local subject="[ALERTE] $1"
    local message="$2"
    
    # Vérifier si mailx est disponible
    if command -v mailx &> /dev/null; then
        echo -e "$message" | mailx -s "$subject" "$EMAIL_TO"
        log "Alerte envoyée à $EMAIL_TO"
    else
        log "${YELLOW}ATTENTION: Impossible d'envoyer une alerte par email (mailx non disponible)${NC}"
    fi
}

# Fonction pour générer un rapport d'état
generate_status_report() {
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local hostname=$(hostname)
    local uptime=$(uptime -p | cut -d" " -f2-)
    
    # Obtenir l'état des conteneurs
    local containers_status=$(docker ps --format '{{.Names}}|{{.Status}}' 2>/dev/null | jq -R -s -c 'split("\n") | map(select(. != "")) | map(split("|") | {name: .[0], status: .[1]})' 2>/dev/null || echo "[]")
    
    # Obtenir l'utilisation du disque
    local disk_usage=$(df -h / | awk 'NR==2 {print $5 "|" $3 "|" $4 "|" $2}' | jq -R 'split("|") | {usage: .[0], used: .[1], available: .[2], total: .[3]}' 2>/dev/null || echo "{}")
    
    # Obtenir l'utilisation de la mémoire
    local memory_info=$(free -m | awk 'NR==2 {print $3 "|" $4 "|" $2}' | jq -R 'split("|") | {used_mb: .[0], free_mb: .[1], total_mb: .[2]}' 2>/dev/null || echo "{}")
    
    # Obtenir l'utilisation du CPU
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}' | cut -d'.' -f1)
    
    # Créer le rapport JSON
    local report={
        "timestamp": "$timestamp",
        "hostname": "$hostname",
        "uptime": "$uptime",
        "cpu_usage_percent": $cpu_usage,
        "disk": $disk_usage,
        "memory": $memory_info,
        "containers": $containers_status,
        "alerts": []
    }
    
    # Enregistrer le rapport dans un fichier
    echo "$report" > "$STATUS_FILE"
    
    log "Rapport d'état généré: $STATUS_FILE"
}

# Fonction pour afficher l'aide
show_help() {
    echo "Utilisation: $0 [options]"
    echo "Options disponibles:"
    echo "  --all            Effectuer toutes les vérifications (par défaut)"
    echo "  --containers     Vérifier les conteneurs Docker"
    echo "  --disk           Vérifier l'utilisation du disque"
    echo "  --memory         Vérifier l'utilisation de la mémoire"
    echo "  --cpu            Vérifier l'utilisation du CPU"
    echo "  --db             Vérifier l'état de la base de données"
    echo "  --redis          Vérifier l'état de Redis"
    echo "  --web            Vérifier l'état de l'application web"
    echo "  --report         Générer un rapport d'état JSON"
    echo "  --help           Afficher cette aide"
    echo ""
    echo "Exemple: $0 --disk --memory --cpu"
}

# Fonction principale
main() {
    # Initialiser les logs
    init_logs
    
    log "=== Début de la surveillance ==="
    log "Heure: $(date '+%Y-%m-%d %H:%M:%S')"
    log "Hôte: $(hostname)"
    log "Répertoire de log: $LOG_FILE"
    
    # Vérifier les arguments de la ligne de commande
    if [ $# -eq 0 ]; then
        # Aucun argument, tout vérifier
        check_containers
        check_disk_usage
        check_memory_usage
        check_cpu_usage
        check_database
        check_redis
        check_web_application
        generate_status_report
    else
        # Vérifier les options spécifiées
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --all)
                    check_containers
                    check_disk_usage
                    check_memory_usage
                    check_cpu_usage
                    check_database
                    check_redis
                    check_web_application
                    generate_status_report
                    shift
                    ;;
                --containers)
                    check_containers
                    shift
                    ;;
                --disk)
                    check_disk_usage
                    shift
                    ;;
                --memory)
                    check_memory_usage
                    shift
                    ;;
                --cpu)
                    check_cpu_usage
                    shift
                    ;;
                --db)
                    check_database
                    shift
                    ;;
                --redis)
                    check_redis
                    shift
                    ;;
                --web)
                    check_web_application
                    shift
                    ;;
                --report)
                    generate_status_report
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
    fi
    
    log "=== Fin de la surveillance ===\n"
}

# Exécuter la fonction principale avec les arguments
main "$@"
