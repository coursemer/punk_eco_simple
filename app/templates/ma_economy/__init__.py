"""Modèles de vues pour le tableau de bord économique marocain.

Ce package contient les modèles de vues spécifiques au tableau de bord
des indicateurs économiques marocains.
"""

# Ce fichier permet d'organiser les modèles de vues pour le tableau de bord économique
# Les modèles sont chargés automatiquement par Flask

# Structure des dossiers recommandée :
# /templates/ma_economy
#   dashboard.html      # Modèle principal du tableau de bord
#   /partials           # Partiels réutilisables
#     _indicators.html   # Vue des indicateurs clés
#     _charts.html       # Graphiques et visualisations
#     _table.html        # Tableau des données

# Exemple d'utilisation dans une vue :
# return render_template('ma_economy/dashboard.html', title='Tableau de bord économique')

__all__ = []  # Aucun import direct depuis ce package
