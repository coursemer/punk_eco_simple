"""
Module pour la gestion des ressources de l'API v1.
Contient les endpoints pour la gestion des ressources de l'application.
"""

from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required
import os
from werkzeug.utils import secure_filename

def init_resources_routes(api_bp):
    """Initialise les routes de gestion des ressources.
    
    Args:
        api_bp: Le blueprint de l'API
    """
    @api_bp.route('/resources', methods=['GET'])
    @jwt_required()
    def get_resources():
        """Récupère la liste des ressources."""
        # Ici, vous pourriez implémenter une logique pour récupérer les ressources
        # depuis une base de données ou un système de stockage
        
        # Pour l'instant, nous retournons une liste vide
        return jsonify({
            'items': [],
            'total': 0,
            'status': 'success'
        })
    
    @api_bp.route('/resources/upload', methods=['POST'])
    @jwt_required()
    def upload_resource():
        """Télécharge une nouvelle ressource."""
        # Vérifier si la requête contient un fichier
        if 'file' not in request.files:
            return jsonify({
                'error': 'Aucun fichier fourni',
                'status': 'error'
            }), 400
        
        file = request.files['file']
        
        # Vérifier si un fichier a été sélectionné
        if file.filename == '':
            return jsonify({
                'error': 'Aucun fichier sélectionné',
                'status': 'error'
            }), 400
        
        # Vérifier l'extension du fichier (exemple avec des images)
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}
        if '.' not in file.filename or \
           file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({
                'error': 'Type de fichier non autorisé',
                'status': 'error',
                'allowed_extensions': list(allowed_extensions)
            }), 400
        
        # Sécuriser le nom du fichier
        filename = secure_filename(file.filename)
        
        # Créer un dossier de téléchargement s'il n'existe pas
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resources')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Sauvegarder le fichier
        filepath = os.path.join(upload_folder, filename)
        
        # Gérer les doublons
        counter = 1
        name, ext = os.path.splitext(filename)
        while os.path.exists(filepath):
            filename = f"{name}_{counter}{ext}"
            filepath = os.path.join(upload_folder, filename)
            counter += 1
        
        try:
            file.save(filepath)
            
            # Ici, vous pourriez enregistrer les métadonnées du fichier dans la base de données
            # Par exemple :
            # resource = Resource(
            #     filename=filename,
            #     filepath=filepath,
            #     user_id=get_jwt_identity(),
            #     size=os.path.getsize(filepath),
            #     mime_type=file.content_type
            # )
            # db.session.add(resource)
            # db.session.commit()
            
            return jsonify({
                'message': 'Fichier téléchargé avec succès',
                'filename': filename,
                'filepath': filepath,
                'status': 'success'
            }), 201
            
        except Exception as e:
            current_app.logger.error(f'Erreur lors du téléchargement du fichier: {str(e)}')
            return jsonify({
                'error': 'Une erreur est survenue lors du téléchargement du fichier',
                'status': 'error'
            }), 500
    
    @api_bp.route('/resources/<resource_id>', methods=['GET'])
    @jwt_required()
    def get_resource(resource_id):
        """Récupère les détails d'une ressource spécifique."""
        # Ici, vous pourriez implémenter la logique pour récupérer une ressource spécifique
        # Par exemple :
        # resource = Resource.query.get_or_404(resource_id)
        # return jsonify(resource.to_dict())
        
        return jsonify({
            'message': f'Détails de la ressource {resource_id} (non implémenté)',
            'status': 'success'
        })
    
    @api_bp.route('/resources/<resource_id>', methods=['PUT'])
    @jwt_required()
    def update_resource(resource_id):
        """Met à jour une ressource existante."""
        # Ici, vous pourriez implémenter la logique de mise à jour d'une ressource
        
        return jsonify({
            'message': f'Ressource {resource_id} mise à jour (non implémenté)',
            'status': 'success'
        })
    
    @api_bp.route('/resources/<resource_id>', methods=['DELETE'])
    @jwt_required()
    def delete_resource(resource_id):
        """Supprime une ressource."""
        # Ici, vous pourriez implémenter la logique de suppression d'une ressource
        # Par exemple :
        # resource = Resource.query.get_or_404(resource_id)
        # db.session.delete(resource)
        # db.session.commit()
        
        return jsonify({
            'message': f'Ressource {resource_id} supprimée (non implémenté)',
            'status': 'success'
        }), 204
