"""
Utilitaires pour l'intégration de Dash dans Flask.

Ce module fournit des fonctions pour faciliter l'intégration de Dash
dans une application Flask existante.
"""

def register_dashapp(app, title, base_pathname, layout, callbacks_fun):
    """Enregistre une application Dash dans une application Flask existante.
    
    Args:
        app: L'application Flask
        title: Titre de l'application Dash
        base_pathname: Chemin de base pour l'application Dash
        layout: Fonction qui retourne le layout de l'application Dash
        callbacks_fun: Fonction pour enregistrer les callbacks de l'application Dash
        
    Returns:
        L'application Dash configurée
    """
    from dash import Dash
    import dash_bootstrap_components as dbc
    
    # Configuration de l'application Dash
    dash_app = Dash(
        __name__,
        server=app,
        url_base_pathname=base_pathname,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
        ],
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ]
    )
    
    # Configuration du titre
    dash_app.title = f"{title} | {app.name}"
    
    # Configuration du layout
    dash_app.layout = layout()
    
    # Enregistrement des callbacks
    callbacks_fun(dash_app)
    
    # Désactiver les callbacks par défaut qui peuvent causer des problèmes
    dash_app.config.suppress_callback_exceptions = True
    
    return dash_app

def create_navbar(title, brand=None):
    """Crée une barre de navigation Bootstrap pour une application Dash.
    
    Args:
        title: Titre de la page
        brand: Texte de la marque (optionnel)
        
    Returns:
        Un composant dbc.Navbar
    """
    import dash_bootstrap_components as dbc
    from dash import html
    
    brand = brand or title
    
    navbar = dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand(brand, href="/"),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink("Accueil", href="/")),
                            dbc.NavItem(dbc.NavLink("Tableau de Bord", href="/dashboard")),
                            dbc.NavItem(dbc.NavLink("Documentation", href="/docs")),
                        ],
                        className="ms-auto",
                        navbar=True,
                    ),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ]
        ),
        color="primary",
        dark=True,
        className="mb-4",
    )
    
    return navbar

def create_footer():
    """Crée un pied de page pour une application Dash.
    
    Returns:
        Un composant dbc.Container avec le pied de page
    """
    import dash_bootstrap_components as dbc
    from dash import html
    from datetime import datetime
    
    return dbc.Container(
        dbc.Row(
            dbc.Col(
                [
                    html.Hr(),
                    html.P(
                        [
                            f"© {datetime.now().year} Punk Eco - "
                            "Tableau de Bord Économique Marocain"
                        ],
                        className="text-center text-muted"
                    )
                ]
            )
        ),
        className="mt-5"
    )

def create_loading_component():
    """Crée un composant de chargement pour les callbacks Dash.
    
    Returns:
        Un composant dbc.Spinner
    """
    import dash_bootstrap_components as dbc
    
    return dbc.Spinner(
        color="primary",
        type="grow",
        fullscreen=True,
        spinner_style={"width": "3rem", "height": "3rem"},
        children=[html.Div(className="visually-hidden", children="Chargement...")]
    )
