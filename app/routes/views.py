"""
Vues de l'application Punk Eco.
"""

from flask import render_template, jsonify, request, make_response, current_app
from . import main

@main.route('/')
def index():
    """Page d'accueil de l'application."""
    return render_template('index.html')

@main.route('/api/status')
def api_status():
    """Endpoint pour vérifier le statut de l'API."""
    return jsonify({
        'status': 'ok',
        'message': 'Punk Eco API is running',
        'version': '0.1.0'
    })

@main.route('/offline')
def offline():
    """Page affichée lorsque l'utilisateur est hors ligne."""
    return render_template('offline.html')

@main.route('/robots.txt')
def robots():
    """Route pour le fichier robots.txt"""
    return current_app.send_static_file('robots.txt')

@main.route('/sitemap.xml')
def sitemap():
    """Génère un sitemap XML pour le référencement"""
    base_url = request.url_root.rstrip('/')
    
    # Liste des URLs du site
    urls = [
        {'loc': base_url, 'changefreq': 'daily', 'priority': '1.0'},
        {'loc': f"{base_url}/about", 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': f"{base_url}/contact", 'changefreq': 'monthly', 'priority': '0.7'},
        # Ajoutez ici d'autres URLs de votre site
    ]
    
    # Créer le XML du sitemap
    sitemap_xml = render_template('sitemap.xml', urls=urls, base_url=base_url)
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response
