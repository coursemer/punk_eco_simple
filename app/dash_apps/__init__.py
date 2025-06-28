"""
Applications Dash pour le tableau de bord économique marocain.

Ce package contient les applications Dash utilisées pour visualiser
les indicateurs économiques marocains.
"""

# Import des applications Dash
from .ma_economy_dash import init_dash as init_ma_economy_dash

__all__ = ['init_ma_economy_dash']
