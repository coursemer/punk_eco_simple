# Guide de maintenance de Punk Eco

Ce document fournit des informations sur les tâches de maintenance courantes, la surveillance et le dépannage de l'application Punk Eco.

## Table des matières

1. [Surveillance du système](#surveillance-du-système)
2. [Maintenance préventive](#maintenance-préventive)
3. [Tâches planifiées](#tâches-planifiées)
4. [Nettoyage](#nettoyage)
5. [Sécurité](#sécurité)
6. [Performances](#performances)
7. [Dépannage](#dépannage)
8. [Journalisation](#journalisation)
9. [Sauvegarde et restauration](#sauvegarde-et-restauration)
10. [Contacts d'urgence](#contacts-durgence)

## Surveillance du système

### Métriques à surveiller

1. **Utilisation du CPU** : Doit rester en dessous de 80% en moyenne
2. **Utilisation de la mémoire** : Doit rester en dessous de 80% de la mémoire disponible
3. **Espace disque** : Garder au moins 20% d'espace libre
4. **Charge du système** : Doit rester en dessous du nombre de cœurs CPU
5. **Taux d'erreur HTTP** : Doit être inférieur à 1%
6. **Temps de réponse** : Le 95e centile doit être inférieur à 500ms

### Outils recommandés

- **Netdata** : Surveillance en temps réel
  ```bash
  # Accéder à l'interface web
  http://votre-serveur:19999
  ```

- **Prometheus + Grafana** : Surveillance et alerting avancés
  ```bash
  # Vérifier les métriques exposées
  curl http://localhost:9100/metrics
  ```

- **Logstash + Elasticsearch + Kibana (ELK)** : Centralisation des logs

## Maintenance préventive

### Tâches quotidiennes

1. **Vérifier les mises à jour de sécurité**
   ```bash
   sudo apt update
   sudo apt list --upgradable
   ```

2. **Vérifier l'état des sauvegardes**
   ```bash
   ls -lh /var/backups/punk_eco/
   ```

3. **Vérifier l'espace disque**
   ```bash
   df -h
   du -sh /var/lib/docker/
   ```

### Tâches hebdomadaires

1. **Nettoyer les conteneurs et images inutilisés**
   ```bash
   docker system prune -f
   docker volume prune -f
   ```

2. **Vérifier la fragmentation de la base de données**
   ```bash
   docker-compose exec db psql -U punk_eco -c "VACUUM ANALYZE;"
   ```

3. **Vérifier les certificats SSL**
   ```bash
   sudo certbot certificates
   ```

### Tâches mensuelles

1. **Mettre à jour le système d'exploitation**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Réviser les accès utilisateurs**
   ```bash
   sudo grep -i "Accepted\|Failed" /var/log/auth.log
   ```

3. **Vérifier les politiques de sécurité**
   ```bash
   sudo ufw status verbose
   sudo fail2ban-client status
   ```

## Tâches planifiées

### Configuration Crontab

```bash
# Éditer le crontab de l'utilisateur punk_eco
sudo -u punk_eco crontab -e
```

### Tâches recommandées

```
# Sauvegarde quotidienne de la base de données à minuit
0 0 * * * /home/punk_eco/punk-eco/backup.sh --db-only >> /var/log/punk_eco/backup.log 2>&1

# Nettoyage des sauvegardes de plus de 30 jours le dimanche à 1h
0 1 * * 0 find /var/backups/punk_eco/ -type f -name "*.sql.gz" -mtime +30 -delete

# Vérification de l'état des services toutes les 5 minutes
*/5 * * * * /home/punk_eco/punk-eco/monitoring.sh --quick >> /var/log/punk_eco/monitoring.log 2>&1

# Renouvellement automatique des certificats Let's Encrypt (vérification deux fois par jour)
0 12,23 * * * /usr/bin/certbot renew --quiet --deploy-hook "systemctl reload nginx"
```

## Nettoyage

### Nettoyage de Docker

```bash
# Supprimer les conteneurs arrêtés
docker container prune -f

# Supprimer les images non utilisées
docker image prune -f

# Supprimer les volumes non utilisés
docker volume prune -f

# Supprimer les réseaux non utilisés
docker network prune -f

# Supprimer tous les éléments non utilisés
docker system prune -a --volumes
```

### Nettoyage des logs

```bash
# Vider les logs des conteneurs
truncate -s 0 /var/lib/docker/containers/*/*-json.log

# Nettoyer les logs système
sudo journalctl --vacuum-time=7d
```

## Sécurité

### Vérifications de sécurité

```bash
# Vérifier les ports ouverts
sudo ss -tulnp

# Vérifier les connexions établies
sudo netstat -tulnp

# Analyser les vulnérabilités avec Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image punk-eco-web:latest
```

### Mise à jour des images Docker

```bash
# Mettre à jour toutes les images
docker-compose pull

# Reconstruire les conteneurs
docker-compose up -d --build
```

## Performances

### Optimisation de la base de données

```bash
# Analyser les requêtes lentes
docker-compose exec db psql -U punk_eco -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Vérifier les index manquants
docker-compose exec db psql -U punk_eco -c "SELECT * FROM pg_stat_user_tables WHERE seq_scan > 0 ORDER BY seq_scan DESC;"
```

### Optimisation de l'application

1. **Activer le cache**
   ```python
   # Dans config.py
   CACHE_TYPE = 'RedisCache'
   CACHE_REDIS_URL = 'redis://redis:6379/0'
   ```

2. **Optimiser les requêtes**
   ```python
   # Activer le débogage des requêtes lentes
   SQLALCHEMY_RECORD_QUERIES = True
   DATABASE_QUERY_TIMEOUT = 0.5  # secondes
   ```

## Dépannage

### Problèmes courants

#### L'application ne démarre pas

```bash
# Voir les logs de l'application
docker-compose logs -f web

# Vérifier les conteneurs en cours d'exécution
docker-compose ps

# Tester la connexion à la base de données
docker-compose exec db pg_isready -U punk_eco
```

#### Problèmes de base de données

```bash
# Se connecter à la base de données
docker-compose exec db psql -U punk_eco

# Vérifier les connexions actives
SELECT * FROM pg_stat_activity;

# Annuler les transactions bloquantes
SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction';
```

#### Problèmes de réseau

```bash
# Vérifier la connectivité réseau
docker-compose exec web ping db
docker-compose exec web curl -I http://web:5000/health

# Inspecter le réseau Docker
docker network inspect punk-eco_default
```

## Journalisation

### Configuration des logs

```yaml
# Dans docker-compose.yml
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Consultation des logs

```bash
# Afficher les logs en temps réel
docker-compose logs -f

# Afficher les 100 dernières lignes des logs
docker-compose logs --tail=100

# Filtrer les logs par service
docker-compose logs web
docker-compose logs db

# Voir les logs système
sudo journalctl -u docker.service -f
```

## Sauvegarde et restauration

### Sauvegarde complète

```bash
# Sauvegarder la base de données
./backup.sh --db-only

# Sauvegarder les fichiers média
./backup.sh --media-only

# Sauvegarder la configuration
./backup.sh --config-only
```

### Restauration

```bash
# Restaurer la base de données
./restore.sh --db backup_file.sql

# Restaurer les fichiers média
./restore.sh --media backup_file.tar.gz
```

## Contacts d'urgence

En cas de problème critique, contactez :

- **Support technique** : support@punk-eco.ma (24/7)
- **Urgences sécurité** : security@punk-eco.ma
- **Responsable infrastructure** : infra@punk-eco.ma

### Procédure d'urgence

1. **Évaluer l'impact**
2. **Contenir le problème**
3. **Documenter les actions**
4. **Notifier les parties prenantes**
5. **Post-mortem et analyse**

### Numéros d'urgence

- **Hébergeur** : +212 XXX XXX XXX
- **Sauvegarde externe** : +212 XXX XXX XXX
