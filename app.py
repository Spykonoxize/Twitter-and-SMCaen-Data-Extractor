import os
import tempfile
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from config import Config
from src.twitter.extractor import extract_twitter_features
from src.caen.extractor import extract_caen_data

app = Flask(__name__)
app.config.from_object(Config)

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Affiche la page principale"""
    return render_template('index.html')

@app.route('/extract-twitter', methods=['POST'])
def extract_twitter():
    """Traite l'extraction de features Twitter"""
    filepath = None
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
        
        # Envoyer le fichier à l'utilisateur
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f'tweets_extracted.{output_format}'
        )
    
    except Exception as e:
        return jsonify({'error': f'Erreur lors du traitement: {str(e)}'}), 500
    
    finally:
        # Nettoyer le fichier temporaire uploadé
        if filepath and os.path.exists(filepath):
            os.remove(filepath)

@app.route('/extract-caen', methods=['POST'])
def extract_caen():
    """Traite l'extraction de données SM Caen"""
    try:
        # Récupérer les paramètres
        annee_debut = int(request.form.get('annee_debut'))
        annee_fin = int(request.form.get('annee_fin'))
        output_format = request.form.get('output_format', 'xlsx')
        
        if annee_debut > annee_fin:
            return jsonify({'error': 'L\'année de début doit être antérieure à l\'année de fin'}), 400
        
        # Extraire les données Caen
        output_path = extract_caen_data(annee_debut, annee_fin, output_format)
        
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

if __name__ == '__main__':
    app.run(debug=False)
