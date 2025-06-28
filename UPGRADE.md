# Guide de mise à jour de Punk Eco

Ce document fournit des instructions détaillées pour effectuer des mises à jour majeures de l'application Punk Eco, y compris les mises à jour de version, les migrations de base de données et les changements de configuration importants.

## Table des matières

1. [Avant de commencer](#avant-de-commencer)
2. [Workflow de mise à jour](#workflow-de-mise-à-jour)
3. [Mise à jour des dépendances](#mise-à-jour-des-dépendances)
4. [Migrations de base de données](#migrations-de-base-de-données)
5. [Mises à jour majeures](#mises-à-jour-majeures)
6. [Rollback](#rollback)
7. [Vérification post-mise à jour](#vérification-post-mise-à-jour)

## Avant de commencer

### Vérification des prérequis

- Vérifiez que vous avez une sauvegarde récente de la base de données
- Assurez-vous d'avoir suffisamment d'espace disque pour la mise à jour
- Vérifiez les notes de version pour les changements importants
- Planifiez une fenêtre de maintenance si nécessaire

### Sauvegarde complète

Avant toute mise à jour, effectuez une sauvegarde complète :

```bash
# Se connecter en tant qu'utilisateur punk_eco
sudo su - punk_eco
cd ~/punk-eco

# Sauvegarder la base de données
./backup.sh --db-only

# Sauvegarder les fichiers média
./backup.sh --media-only
```

## Workflow de mise à jour

### 1. Mettre à jour le code source

```bash
# Se déplacer dans le répertoire de l'application
cd ~/punk-eco

# Arrêter les conteneurs
docker-compose down

# Sauvegarder l'ancienne version (optionnel mais recommandé)
git checkout -b backup-$(date +%Y%m%d)
git push origin backup-$(date +%Y%m%d)

# Passer à la branche principale
git checkout main

# Mettre à jour le code source
git fetch origin
git reset --hard origin/main
```

### 2. Mettre à jour les dépendances

```bash
# Vérifier les nouvelles dépendances
cat requirements.txt

# Reconstruire les images Docker
docker-compose build --no-cache
```

### 3. Mettre à jour la configuration

Vérifiez si des changements de configuration sont nécessaires :

```bash
# Voir les changements dans le fichier .env.example
git diff --no-index .env.example .env.example.old || true

# Mettre à jour votre fichier .env si nécessaire
nano .env
```

### 4. Mettre à jour la base de données

```bash
# Appliquer les migrations
docker-compose run --rm web flask db upgrade
```

### 5. Redémarrer les services

```bash
# Démarrer les services en arrière-plan
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

## Mise à jour des dépendances

### Mise à jour des dépendances Python

1. Mettez à jour les dépendances dans `requirements.txt`
2. Reconstruisez l'image Docker :

```bash
docker-compose build --no-cache
```

### Mise à jour des dépendances JavaScript

Si vous avez modifié `package.json` :

```bash
# Reconstruire l'image pour installer les nouvelles dépendances
docker-compose build --no-cache

# Redémarrer les services
docker-compose up -d
```

## Migrations de base de données

### Créer une nouvelle migration

```bash
# Créer un fichier de migration vide
docker-compose run --rm web flask db migrate -m "Description des changements"

# Vérifier le fichier de migration généré
ls -l migrations/versions/
```

### Appliquer les migrations

```bash
# Appliquer toutes les migrations en attente
docker-compose run --rm web flask db upgrade
```

### Annuler une migration

```bash
# Revenir à une version précédente
docker-compose run --rm web flask db downgrade <revision>
```

## Mises à jour majeures

### Mise à jour vers une nouvelle version majeure

1. **Lisez attentivement les notes de version** pour les changements importants
2. **Testez la mise à jour dans un environnement de staging**
3. **Planifiez une fenêtre de maintenance**
4. **Sauvegardez tout** avant de procéder

### Exemple : Mise à jour de v1.x vers v2.0

```bash
# 1. Mettre à jour le code source
git fetch origin
git checkout v2.0.0

# 2. Mettre à jour les dépendances
docker-compose build --no-cache

# 3. Appliquer les migrations
docker-compose run --rm web flask db upgrade

# 4. Redémarrer les services
docker-compose up -d
```

## Rollback

En cas de problème, vous pouvez revenir à la version précédente :

```bash
# Arrêter les conteneurs
docker-compose down

# Revenir à la version précédente
git checkout <previous-tag-or-commit>

# Reconstruire les images
docker-compose build --no-cache

# Restaurer la base de données si nécessaire
docker-compose run --rm web flask db downgrade <previous-revision>

# Redémarrer les services
docker-compose up -d
```

## Vérification post-mise à jour

Après la mise à jour, vérifiez que tout fonctionne correctement :

1. **Vérifiez les logs** pour des erreurs
   ```bash
   docker-compose logs -f
   ```

2. **Testez les fonctionnalités principales**
   - Connexion utilisateur
   - Accès aux données
   - Fonctionnalités critiques

3. **Vérifiez les performances**
   ```bash
   # Voir l'utilisation des ressources
   docker stats
   ```

4. **Surveillez les erreurs** dans les logs d'application

## Dépannage des problèmes courants

### Problèmes de migration

```bash
# Afficher l'état actuel des migrations
docker-compose run --rm web flask db current

# Annuler la dernière migration
docker-compose run --rm web flask db downgrade -1

# Forcer une révision spécifique
docker-compose run --rm web flask db stamp <revision>
```

### Problèmes de dépendances

```bash
# Reconstruire l'image avec un cache propre
docker-compose build --no-cache

# Vérifier les dépendances installées
docker-compose run --rm web pip freeze
```

### Problèmes de démarrage

```bash
# Voir les logs détaillés
docker-compose logs -f

# Vérifier l'état des conteneurs
docker-compose ps

# Tester la connexion à la base de données
docker-compose exec db pg_isready -U punk_eco
```

## Mises à jour automatisées

Pour les mises à jour mineures, vous pouvez utiliser le script `update.sh` :

```bash
# Mise à jour simple
./update.sh

# Mise à jour avec sauvegarde
./update.sh --backup

# Mise à jour sans redémarrage des services
./update.sh --no-restart
```

## Notes importantes

- **Toujours tester les mises à jour majeures dans un environnement de staging**
- **Sauvegardez toujours vos données avant de procéder à une mise à jour**
- **Documentez les changements** dans le fichier CHANGELOG.md
- **Informez les utilisateurs** des temps d'arrêt prévus

## Support

Pour toute question ou problème lié aux mises à jour, veuillez ouvrir une issue sur [notre dépôt GitHub](https://github.com/votre-utilisateur/punk-eco/issues) ou nous contacter à support@punk-eco.ma.
