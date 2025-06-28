# Guide d'installation et de déploiement de Punk Eco

Ce guide vous guidera à travers le processus d'installation et de déploiement de l'application Punk Eco sur un serveur de production.

## Table des matières

1. [Prérequis](#prérequis)
2. [Configuration du serveur](#configuration-du-serveur)
3. [Installation de l'application](#installation-de-lapplication)
4. [Configuration de la base de données](#configuration-de-la-base-de-données)
5. [Configuration du serveur web](#configuration-du-serveur-web)
6. [Configuration SSL](#configuration-ssl)
7. [Démarrage des services](#démarrage-des-services)
8. [Mises à jour](#mises-à-jour)
9. [Sauvegarde et restauration](#sauvegarde-et-restauration)
10. [Dépannage](#dépannage)

## Prérequis

- Un serveur Ubuntu 20.04 LTS ou plus récent
- Au moins 2 Go de RAM (4 Go recommandés)
- Au moins 20 Go d'espace disque
- Un nom de domaine pointant vers l'IP de votre serveur
- Un accès root ou un utilisateur avec des privilèges sudo

## Configuration du serveur

### 1. Mise à jour du système

```bash
# Mettre à jour la liste des paquets
sudo apt update

# Mettre à niveau les paquets installés
sudo apt upgrade -y

# Installer les paquets de base
sudo apt install -y curl wget git unzip
```

### 2. Configuration du fuseau horaire

```bash
# Définir le fuseau horaire (remplacez Europe/Paris par votre fuseau horaire)
sudo timedatectl set-timezone Europe/Paris

# Vérifier le fuseau horaire
timedatectl
```

### 3. Configuration du pare-feu

```bash
# Installer UFW (Uncomplicated Firewall)
sudo apt install -y ufw

# Configurer les règles de base
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Autoriser SSH (changez le port si nécessaire)
sudo ufw allow 22/tcp

# Autoriser HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activer le pare-feu
sudo ufw enable

# Vérifier l'état du pare-feu
sudo ufw status
```

### 4. Configuration du swap (si nécessaire)

```bash
# Vérifier si le swap est déjà configuré
free -h

# Si nécessaire, créer un fichier de swap (2x la taille de la RAM)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Rendre le swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Optimiser les paramètres de swap
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## Installation de l'application

### 1. Installer Docker et Docker Compose

```bash
# Installer les dépendances
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Ajouter la clé GPG officielle de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Ajouter le dépôt Docker
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Mettre à jour les paquets et installer Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Vérifier l'installation
sudo docker --version

# Installer Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Vérifier l'installation
docker-compose --version
```

### 2. Créer un utilisateur pour l'application

```bash
# Créer un nouvel utilisateur
sudo adduser --gecos "" punk_eco

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker punk_eco

# Passer à l'utilisateur punk_eco
sudo su - punk_eco
```

### 3. Cloner le dépôt

```bash
# Se déplacer dans le répertoire personnel
cd ~

# Cloner le dépôt (remplacez par l'URL de votre dépôt)
git clone https://github.com/votre-utilisateur/punk-eco.git
cd punk-eco
```

### 4. Configurer les variables d'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env avec vos paramètres
nano .env
```

Assurez-vous de configurer au moins les variables suivantes :

```
# Application
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=votre_clé_secrète_très_longue_et_aléatoire

# Base de données
POSTGRES_USER=punk_eco
POSTGRES_PASSWORD=un_mot_de_passe_sécurisé
POSTGRES_DB=punk_eco
DATABASE_URL=postgresql://punk_eco:un_mot_de_passe_sécurisé@db:5432/punk_eco

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=votre@email.com
MAIL_PASSWORD=votre_mot_de_passe_email

# Domaine
DOMAIN=votredomaine.com
```

## Configuration de la base de données

### 1. Démarrer les services

```bash
# Démarrer les conteneurs en arrière-plan
docker-compose up -d db redis

# Vérifier que les conteneurs sont en cours d'exécution
docker-compose ps
```

### 2. Initialiser la base de données

```bash
# Créer les tables de la base de données
docker-compose exec web flask db upgrade

# Créer un utilisateur administrateur
docker-compose exec web flask create-admin admin@example.com motdepasse
```

## Configuration du serveur web

### 1. Installer et configurer Nginx

```bash
# Installer Nginx
sudo apt install -y nginx

# Arrêter Nginx
sudo systemctl stop nginx

# Supprimer la configuration par défaut
sudo rm -f /etc/nginx/sites-enabled/default

# Créer un fichier de configuration pour Punk Eco
sudo nano /etc/nginx/sites-available/punk-eco
```

Ajoutez la configuration suivante (remplacez `votredomaine.com` par votre domaine) :

```nginx
upstream punk_eco {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name votredomaine.com www.votredomaine.com;
    
    location / {
        proxy_pass http://punk_eco;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /home/punk_eco/punk-eco/app/static/;
        expires 30d;
    }
    
    location /media/ {
        alias /home/punk_eco/punk-eco/instance/media/;
        expires 30d;
    }
}
```

Activez le site et testez la configuration :

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/punk-eco /etc/nginx/sites-enabled/

# Tester la configuration Nginx
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
```

## Configuration SSL

### 1. Installer Certbot

```bash
# Installer Certbot et le plugin Nginx
sudo apt install -y certbot python3-certbot-nginx

# Obtenir un certificat SSL (remplacez l'email et le domaine)
sudo certbot --nginx -d votredomaine.com -d www.votredomaine.com --email votre@email.com --agree-tos --no-eff-email --redirect

# Configurer le renouvellement automatique
sudo systemctl status certbot.timer
```

### 2. Mettre à jour la configuration Nginx

La commande Certbot a dû mettre à jour votre configuration Nginx. Vérifiez qu'elle ressemble à ceci :

```nginx
server {
    server_name votredomaine.com www.votredomaine.com;

    location / {
        proxy_pass http://punk_eco;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/punk_eco/punk-eco/app/static/;
        expires 30d;
    }

    location /media/ {
        alias /home/punk_eco/punk-eco/instance/media/;
        expires 30d;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/votredomaine.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/votredomaine.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if ($host = www.votredomaine.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    if ($host = votredomaine.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    server_name votredomaine.com www.votredomaine.com;
    return 404; # managed by Certbot
}
```

## Démarrage des services

### 1. Démarrer l'application

```bash
# Se connecter en tant qu'utilisateur punk_eco
sudo su - punk_eco
cd ~/punk-eco

# Démarrer les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

### 2. Configurer le démarrage automatique

Créez un fichier de service systemd pour démarrer automatiquement l'application au démarrage du serveur :

```bash
# Créer un fichier de service
sudo nano /etc/systemd/system/punk-eco.service
```

Ajoutez le contenu suivant (mettez à jour les chemins si nécessaire) :

```ini
[Unit]
Description=Punk Eco Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/punk_eco/punk-eco
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=punk_eco
Group=punk_eco

[Install]
WantedBy=multi-user.target
```

Activez et démarrez le service :

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer le démarrage automatique
sudo systemctl enable punk-eco.service

# Démarrer le service
sudo systemctl start punk-eco.service

# Vérifier l'état du service
sudo systemctl status punk-eco.service
```

## Mises à jour

### Mettre à jour l'application

```bash
# Se connecter en tant qu'utilisateur punk_eco
sudo su - punk_eco
cd ~/punk-eco

# Arrêter les conteneurs
docker-compose down

# Mettre à jour le code source
git pull

# Reconstruire les images
docker-compose build --no-cache

# Redémarrer les services
docker-compose up -d

# Appliquer les migrations de base de données
docker-compose exec web flask db upgrade
```

### Mettre à jour les dépendances

Si vous avez modifié `requirements.txt` ou `package.json`, reconstruisez l'image :

```bash
docker-compose build --no-cache
docker-compose up -d
```

## Sauvegarde et restauration

### Sauvegarder la base de données

```bash
# Créer un répertoire de sauvegarde
mkdir -p ~/backups

# Exporter la base de données
docker-compose exec db pg_dump -U punk_eco punk_eco > ~/backups/punk_eco_$(date +%Y%m%d).sql

# Compresser la sauvegarde
gzip ~/backups/punk_eco_$(date +%Y%m%d).sql
```

### Restaurer la base de données

```bash
# Décompresser la sauvegarde
gunzip ~/backups/punk_eco_YYYYMMDD.sql.gz

# Restaurer la base de données
cat ~/backups/punk_eco_YYYYMMDD.sql | docker-compose exec -T db psql -U punk_eco -d punk_eco
```

### Sauvegarder les fichiers média

```bash
# Créer une archive des fichiers média
tar -czf ~/backups/punk_eco_media_$(date +%Y%m%d).tar.gz instance/media/
```

### Restaurer les fichiers média

```bash
# Extraire l'archive dans le répertoire média
tar -xzf ~/backups/punk_eco_media_YYYYMMDD.tar.gz -C .
```

## Dépannage

### Vérifier les logs

```bash
# Afficher les logs de l'application
docker-compose logs -f web

# Afficher les logs de la base de données
docker-compose logs -f db

# Afficher les logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

### Vérifier les conteneurs en cours d'exécution

```bash
docker ps
docker-compose ps
```

### Redémarrer les services

```bash
# Redémarrer un service spécifique
docker-compose restart web

# Redémarrer tous les services
docker-compose restart
```

### Se connecter à la base de données

```bash
docker-compose exec db psql -U punk_eco -d punk_eco
```

### Vérifier les erreurs courantes

1. **Erreurs de connexion à la base de données** :
   - Vérifiez que le conteneur de base de données est en cours d'exécution
   - Vérifiez les identifiants dans le fichier `.env`
   - Vérifiez les logs de la base de données

2. **Erreurs 502 Bad Gateway** :
   - Vérifiez que l'application est en cours d'exécution avec `docker-compose ps`
   - Vérifiez les logs de l'application avec `docker-compose logs web`
   - Vérifiez que Nginx peut accéder au conteneur de l'application

3. **Problèmes de permissions** :
   - Assurez-vous que l'utilisateur `www-data` a les droits de lecture sur les fichiers statiques
   - Vérifiez les permissions des répertoires `instance/media` et `app/static`

4. **Erreurs de certificat SSL** :
   - Vérifiez que votre nom de domaine est correctement configuré
   - Renouvelez le certificat avec `sudo certbot renew --dry-run`
   - Vérifiez que le port 443 est ouvert dans le pare-feu

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur [notre dépôt GitHub](https://github.com/votre-utilisateur/punk-eco/issues) ou nous contacter à support@punk-eco.ma.
