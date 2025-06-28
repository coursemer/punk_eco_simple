#!/bin/bash

# Punk Eco - Script de configuration du serveur
# Ce script prépare un nouveau serveur pour l'application Punk Eco

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_USER="punk_eco"
APP_GROUP="$APP_USER"
APP_HOME="/opt/$APP_USER"
APP_LOG_DIR="/var/log/$APP_USER"
APP_BACKUP_DIR="/var/backups/$APP_USER"
APP_SECRETS_DIR="/etc/$APP_USER"

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

# Mettre à jour le système
update_system() {
    info "Mise à jour du système..."
    
    apt-get update && apt-get upgrade -y
    
    if [ $? -eq 0 ]; then
        success "Système mis à jour avec succès"
    else
        error "Échec de la mise à jour du système"
    fi
}

# Installer les dépendances système
install_dependencies() {
    info "Installation des dépendances système..."
    
    apt-get install -y \
        curl \
        wget \
        git \
        unzip \
        htop \
        vim \
        tmux \
        ufw \
        fail2ban \
        ntp \
        ca-certificates \
        apt-transport-https \
        software-properties-common \
        gnupg-agent \
        jq \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        libpq-dev \
        nginx \
        certbot \
        python3-certbot-nginx
    
    if [ $? -eq 0 ]; then
        success "Dépendances système installées avec succès"
    else
        error "Échec de l'installation des dépendances système"
    fi
}

# Configurer le pare-feu
configure_firewall() {
    info "Configuration du pare-feu (UFW)..."
    
    # Activer UFW s'il n'est pas déjà activé
    if ! ufw status | grep -q "Status: active"; then
        ufw --force reset
        ufw default deny incoming
        ufw default allow outgoing
        
        # Autoriser SSH
        ufw allow ssh
        
        # Autoriser HTTP/HTTPS
        ufw allow 80/tcp
        ufw allow 443/tcp
        
        # Activer le pare-feu
        echo "y" | ufw enable
    fi
    
    # Vérifier l'état du pare-feu
    ufw status
    
    success "Pare-feu configuré avec succès"
}

# Configurer le fuseau horaire
configure_timezone() {
    info "Configuration du fuseau horaire..."
    
    timedatectl set-timezone Europe/Paris
    
    # Vérifier le fuseau horaire
    timedatectl
    
    success "Fuseau horaire configuré avec succès"
}

# Installer Docker
install_docker() {
    info "Installation de Docker..."
    
    # Vérifier si Docker est déjà installé
    if command -v docker &> /dev/null; then
        info "Docker est déjà installé"
        return 0
    fi
    
    # Installer les dépendances nécessaires
    apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common
    
    # Ajouter la clé GPG officielle de Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
    
    # Ajouter le dépôt Docker
    add-apt-repository \
       "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
       $(lsb_release -cs) \
       stable"
    
    # Mettre à jour les paquets et installer Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Démarrer et activer Docker au démarrage
    systemctl enable --now docker
    
    # Vérifier l'installation
    docker --version
    
    success "Docker installé avec succès"
}

# Installer Docker Compose
install_docker_compose() {
    info "Installation de Docker Compose..."
    
    # Vérifier si Docker Compose est déjà installé
    if command -v docker-compose &> /dev/null; then
        info "Docker Compose est déjà installé"
        return 0
    fi
    
    # Télécharger la version stable de Docker Compose
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # Rendre le binaire exécutable
    chmod +x /usr/local/bin/docker-compose
    
    # Créer un lien symbolique
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    # Vérifier l'installation
    docker-compose --version
    
    success "Docker Compose installé avec succès"
}

# Créer l'utilisateur de l'application
create_app_user() {
    info "Création de l'utilisateur de l'application..."
    
    # Vérifier si l'utilisateur existe déjà
    if id "$APP_USER" &>/dev/null; then
        info "L'utilisateur $APP_USER existe déjà"
    else
        # Créer l'utilisateur et son groupe
        useradd -m -s /bin/bash -d "$APP_HOME" "$APP_USER"
        
        # Ajouter l'utilisateur au groupe docker
        usermod -aG docker "$APP_USER"
        
        success "Utilisateur $APP_USER créé avec succès"
    fi
    
    # Créer les répertoires nécessaires
    mkdir -p "$APP_LOG_DIR" "$APP_BACKUP_DIR" "$APP_SECRETS_DIR"
    chown -R "$APP_USER:$APP_GROUP" "$APP_LOG_DIR" "$APP_BACKUP_DIR" "$APP_SECRETS_DIR"
    chmod 750 "$APP_LOG_DIR" "$APP_BACKUP_DIR" "$APP_SECRETS_DIR"
    
    # Créer un lien symbolique vers le répertoire de logs dans le home de l'utilisateur
    su - "$APP_USER" -c "ln -s $APP_LOG_DIR ~/logs"
    
    success "Répertoires de l'application créés avec succès"
}

# Configurer SSH
configure_ssh() {
    info "Configuration de SSH..."
    
    # Sauvegarder la configuration SSH existante
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # Désactiver la connexion root
    sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    
    # Désactiver l'authentification par mot de passe
    sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    
    # Activer l'authentification par clé
    sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
    
    # Désactiver X11 Forwarding
    sed -i 's/^X11Forwarding yes/X11Forwarding no/' /etc/ssh/sshd_config
    
    # Configurer les utilisateurs autorisés
    echo "AllowUsers $APP_USER" >> /etc/ssh/sshd_config
    
    # Redémarrer le service SSH
    systemctl restart sshd
    
    success "SSH configuré avec succès"
}

# Configurer le swap
configure_swap() {
    info "Configuration du swap..."
    
    # Vérifier si le swap est déjà configuré
    if swapon --show | grep -q "/"; then
        info "Le swap est déjà configuré"
        return 0
    fi
    
    # Déterminer la taille du swap (1.5x la mémoire RAM)
    RAM_SIZE=$(free -m | awk '/^Mem:/{print $2}')
    SWAP_SIZE=$((RAM_SIZE * 3 / 2))
    
    # Créer le fichier de swap
    fallocate -l ${SWAP_SIZE}M /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    
    # Activer le swap au démarrage
    echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
    
    # Configurer les paramètres sysctl pour le swap
    echo 'vm.swappiness=10' | tee -a /etc/sysctl.conf
    echo 'vm.vfs_cache_pressure=50' | tee -a /etc/sysctl.conf
    
    # Appliquer les modifications
    sysctl -p
    
    success "Swap configuré avec succès (${SWAP_SIZE}M)"
}

# Configurer les limites système
configure_limits() {
    info "Configuration des limites système..."
    
    # Augmenter les limites de fichier
    echo "* soft nofile 65536" | tee -a /etc/security/limits.conf
    echo "* hard nofile 131072" | tee -a /etc/security/limits.conf
    echo "root soft nofile 65536" | tee -a /etc/security/limits.conf
    echo "root hard nofile 131072" | tee -a /etc/security/limits.conf
    
    # Augmenter les limites de processus
    echo "* soft nproc 65536" | tee -a /etc/security/limits.conf
    echo "* hard nproc 131072" | tee -a /etc/security/limits.conf
    echo "root soft nproc 65536" | tee -a /etc/security/limits.conf
    echo "root hard nproc 131072" | tee -a /etc/security/limits.conf
    
    # Pour les systèmes utilisant systemd
    echo "DefaultLimitNOFILE=65536" | tee -a /etc/systemd/system.conf
    echo "DefaultLimitNPROC=65536" | tee -a /etc/systemd/system.conf
    
    # Recharger la configuration systemd
    systemctl daemon-reload
    
    success "Limites système configurées avec succès"
}

# Configurer Nginx
configure_nginx() {
    info "Configuration de Nginx..."
    
    # Arrêter Nginx s'il est en cours d'exécution
    systemctl stop nginx
    
    # Supprimer la configuration par défaut
    rm -f /etc/nginx/sites-enabled/default
    
    # Créer le répertoire pour les certificats SSL
    mkdir -p /etc/letsencrypt/live/punk-eco.ma
    
    # Configurer les paramètres généraux
    cat > /etc/nginx/nginx.conf << 'EOL'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 1024;
    multi_accept on;
    use epoll;
}

http {
    # Paramètres de base
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    # Tailles de buffer
    client_max_body_size 20M;
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;
    
    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;
    
    # Types MIME
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log warn;
    
    # Gzip
    gzip on;
    gzip_disable "msie6";
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Inclure les configurations de site
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOL
    
    # Activer et démarrer Nginx
    systemctl enable nginx
    systemctl start nginx
    
    success "Nginx configuré avec succès"
}

# Configurer le pare-feu applicatif (fail2ban)
configure_fail2ban() {
    info "Configuration de Fail2Ban..."
    
    # Créer un fichier de configuration personnalisé pour Nginx
    cat > /etc/fail2ban/jail.d/nginx.conf << 'EOL'
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port    = http,https
logpath = %(nginx_error_log)s

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
port    = http,https
logpath = %(nginx_error_log)s

[nginx-badbots]
enabled  = true
filter   = apache-badbots
port     = http,https
logpath  = %(nginx_access_log)s
maxretry = 2

[nginx-noscript]
enabled  = true
port    = http,https
filter  = nginx-noscript
logpath = %(nginx_error_log)s
maxretry = 6

[nginx-proxy]
enabled  = true
port    = http,https
filter  = nginx-proxy
logpath = %(nginx_error_log)s
maxretry = 6
EOL
    
    # Redémarrer Fail2Ban
    systemctl restart fail2ban
    
    success "Fail2Ban configuré avec succès"
}

# Installer et configurer le monitoring
install_monitoring() {
    info "Installation des outils de monitoring..."
    
    # Installer les outils de base
    apt-get install -y htop iotop iftop nmon sysstat dstat
    
    # Installer Netdata pour le monitoring en temps réel
    bash <(curl -Ss https://my-netdata.io/kickstart.sh) --stable-channel --disable-telemetry
    
    # Configurer Netdata pour qu'il n'écoute que sur localhost
    sed -i 's/# bind to = \*/bind to = 127.0.0.1/' /etc/netdata/netdata.conf
    
    # Redémarrer Netdata
    systemctl restart netdata
    
    success "Outils de monitoring installés avec succès"
}

# Afficher les instructions de post-installation
post_install_instructions() {
    echo -e "\n${GREEN}=== Installation terminée avec succès ===${NC}\n"
    
    echo -e "${YELLOW}Prochaines étapes:${NC}"
    echo "1. Ajoutez votre clé SSH à ~$APP_USER/.ssh/authorized_keys"
    echo "2. Configurez les variables d'environnement dans $APP_HOME/.env"
    echo "3. Déployez l'application avec le script deploy.sh"
    echo "4. Configurez un certificat SSL avec Certbot"
    echo -e "\n${YELLOW}Accès au monitoring:${NC}"
    echo "- Netdata: http://localhost:19999/"
    echo -e "\n${YELLOW}Connexion SSH:${NC}"
    echo "ssh $APP_USER@$(curl -s ifconfig.me)"
    echo -e "\n${GREEN}=== Punk Eco est prêt à être déployé ! ===${NC}\n"
}

# Fonction principale
main() {
    echo -e "\n${BLUE}=== Démarrage de la configuration du serveur Punk Eco ===${NC}\n"
    
    # Mettre à jour le système
    update_system
    
    # Installer les dépendances
    install_dependencies
    
    # Configurer le fuseau horaire
    configure_timezone
    
    # Configurer le swap
    configure_swap
    
    # Configurer les limites système
    configure_limits
    
    # Installer Docker
    install_docker
    
    # Installer Docker Compose
    install_docker_compose
    
    # Créer l'utilisateur de l'application
    create_app_user
    
    # Configurer SSH
    configure_ssh
    
    # Configurer le pare-feu
    configure_firewall
    
    # Configurer Nginx
    configure_nginx
    
    # Configurer Fail2Ban
    configure_fail2ban
    
    # Installer les outils de monitoring
    install_monitoring
    
    # Afficher les instructions de post-installation
    post_install_instructions
}

# Exécuter la fonction principale
main
