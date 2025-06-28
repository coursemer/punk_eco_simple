# Guide de contribution

Merci de votre intérêt pour contribuer à **Punk Eco** ! Ce guide vous aidera à comprendre comment contribuer efficacement au projet.

## 📋 Avant de commencer

- Assurez-vous d'avoir un compte [GitHub](https://github.com/)
- Lisez le [Code de conduite](CODE_OF_CONDUCT.md)
- Vérifiez les [issues existantes](https://github.com/punk-eco/moroccan-economy-dashboard/issues) pour éviter les doublons

## 🛠 Configuration de l'environnement

1. **Fork** le dépôt sur GitHub
2. Clonez votre fork localement :
   ```bash
   git clone https://github.com/votre-utilisateur/moroccan-economy-dashboard.git
   cd moroccan-economy-dashboard
   ```
3. Configurez le dépôt distant :
   ```bash
   git remote add upstream https://github.com/punk-eco/moroccan-economy-dashboard.git
   ```
4. Installez les dépendances :
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```

## 🔄 Processus de développement

1. **Mettez à jour votre branche principale** :
   ```bash
   git checkout main
   git fetch upstream
   git merge upstream/main
   ```

2. **Créez une branche** pour votre fonctionnalité/correction :
   ```bash
   git checkout -b feature/nom-de-la-fonctionnalite
   # ou
   git checkout -b fix/correction-de-bug
   ```

3. **Codez** votre fonctionnalité ou correction

4. **Vérifiez la qualité du code** :
   ```bash
   make lint
   make test
   ```

5. **Validez vos changements** avec des messages clairs :
   ```bash
   git add .
   git commit -m "Description claire et concise de vos changements"
   ```

6. **Poussez vos changements** vers votre fork :
   ```bash
   git push origin votre-branche
   ```

7. **Créez une Pull Request** vers la branche `main` du dépôt principal

## 📝 Bonnes pratiques

### Commit Messages

- Utilisez la forme impérative ("Add feature" pas "Added feature")
- Limitez la première ligne à 50 caractères
- Détaillez les changements dans le corps du message si nécessaire
- Référencez les numéros d'issue quand c'est pertinent (ex: "Fix #123")

### Style de code

- Suivez [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utilisez [Black](https://black.readthedocs.io/) pour le formatage
- Écrivez des docstrings selon la [convention Google](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Ajoutez des tests unitaires pour les nouvelles fonctionnalités

### Tests

- Exécutez tous les tests avant de soumettre une PR :
  ```bash
  make test
  ```
- La couverture de code doit rester à 100% pour le code nouveau
- Les tests doivent être indépendants et reproductibles

## 🐛 Signaler un bug

1. Vérifiez que le bug n'a pas déjà été signalé
2. Créez une issue avec :
   - Un titre clair et descriptif
   - Les étapes pour reproduire le bug
   - Le comportement attendu
   - Votre configuration (OS, version de Python, etc.)
   - Capture d'écran si pertinent

## 🚀 Proposer une fonctionnalité

1. Vérifiez que la fonctionnalité n'est pas déjà planifiée
2. Créez une issue pour discuter de la fonctionnalité
3. Une fois approuvée, suivez le processus de développement standard

## 📚 Ressources

- [Guide de style Python](https://www.python.org/dev/peps/pep-0008/)
- [Conventions de commit](https://www.conventionalcommits.org/)
- [Documentation de Flask](https://flask.palletsprojects.com/)
- [Documentation SQLAlchemy](https://docs.sqlalchemy.org/)

## 🙋 Questions ?

Si vous avez des questions, n'hésitez pas à :
- Créer une discussion dans les [GitHub Discussions](https://github.com/punk-eco/moroccan-economy-dashboard/discussions)
- Nous contacter à [contact@punk-eco.ma](mailto:contact@punk-eco.ma)

---

Merci de contribuer à rendre ce projet meilleur ! 🎉
