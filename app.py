import os
import tempfile
from flask import Flask, render_template, request, send_file, jsonify, after_this_request
from werkzeug.utils import secure_filename
from config import Config
from src.twitter.extractor import extract_twitter_features
from src.caen.extractor import extract_caen_data
import gc

app = Flask(__name__)
app.config.from_object(Config)

# Configure maximum file size (150MB for safety on 512MB Render)
app.config['MAX_CONTENT_LENGTH'] = 150 * 1024 * 1024


@app.errorhandler(413)
def request_entity_too_large(_error):
    return jsonify({'error': 'Fichier trop volumineux. Limite actuelle: 150 MB.'}), 413


@app.errorhandler(500)
def internal_server_error(_error):
    return jsonify({'error': 'Erreur interne du serveur. Veuillez réessayer.'}), 500

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def cleanup_temp_files():
    """Clean up temporary files to free RAM"""
    temp_dir = app.config['UPLOAD_FOLDER']
    if os.path.exists(temp_dir):
        try:
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception:
            pass
    gc.collect()


def schedule_file_cleanup(file_path):
    """Delete generated file only after the response is fully sent."""

    @after_this_request
    def _cleanup(response):
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return response

@app.route('/')
def index():
    """Affiche la page principale"""
    return render_template('index.html')

@app.route('/extract-twitter', methods=['POST'])
def extract_twitter():
    """Traite l'extraction de features Twitter"""
    filepath = None
    output_path = None
    
    try:
        # Vérifier si un fichier est uploadé
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Type de fichier non autorisé. Utilisez CSV, JSON, XLSX, XLS ou JS'}), 400
        
        # Récupérer les features sélectionnées
        selected_features = request.form.getlist('features')
        output_format = request.form.get('output_format', 'xlsx')
        
        if not selected_features:
            return jsonify({'error': 'Veuillez sélectionner au moins une feature'}), 400
        
        # Sauvegarder temporairement le fichier
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extraire les features et générer le fichier de sortie
        output_path = extract_twitter_features(
            filepath,
            selected_features,
            output_format
        )
        
        # Delete output only after download is completed.
        schedule_file_cleanup(output_path)

        # Envoyer le fichier à l'utilisateur
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f'tweets_extracted.{output_format}'
        )
    
    except Exception as e:
        return jsonify({'error': f'Erreur lors du traitement: {str(e)}'}), 500
    
    finally:
        # Nettoyer les fichiers temporaires
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass
        
        # Force garbage collection
        gc.collect()

@app.route('/extract-caen', methods=['POST'])
def extract_caen():
    """Traite l'extraction de données SM Caen"""
    output_path = None
    
    try:
        # Récupérer les paramètres
        annee_debut = int(request.form.get('annee_debut'))
        annee_fin = int(request.form.get('annee_fin'))
        output_format = request.form.get('output_format', 'xlsx')
        
        if annee_debut > annee_fin:
            return jsonify({'error': 'L\'année de début doit être antérieure à l\'année de fin'}), 400
        
        # Extraire les données Caen
        output_path = extract_caen_data(annee_debut, annee_fin, output_format)
        
        # Delete output only after download is completed.
        schedule_file_cleanup(output_path)

        # Envoyer le fichier à l'utilisateur
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f'caen_data_{annee_debut}_{annee_fin}.{output_format}'
        )
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erreur lors du traitement: {str(e)}'}), 500
    
    finally:
        gc.collect()

if __name__ == '__main__':
    app.run(debug=False)
