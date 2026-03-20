# Data Extractor

Une application web professionnelle pour extraire et exporter des données Twitter et SM Caen (football) en plusieurs formats.

**Interface entièrement en français** | **Déploiement Render prêt** | **Pas de dépendances externes**

## 🎯 Fonctionnalités

### 🐦 Twitter Features Extractor
Parse les données Twitter depuis plusieurs formats (CSV, JSON, XLSX, JS) et extrait 9 features:
- **Contenu**: Texte complet du tweet
- **Date**: Format ISO (YYYY-MM-DD HH:MM:SS)
- **Hashtags**: Extraction depuis entités ou texte
- **Mentions**: Noms d'utilisateurs mentionnés
- **Favoris**: Nombre de likes
- **Retweets**: Nombre de retweets
- **Média**: Détection de présence de média
- **Nombre mentions**: Décompte des mentions
- **Emojis**: Extraction des emojis

### ⚽ SM Caen Extractor
Scrape les données réelles du site officiel de SM Caen et exporte:
- **Saison**: Année(s) de la saison
- **Date & Horaire**: Informations temporelles
- **Compétition**: Type de match
- **Équipes**: Domicile, Extérieur, Adversaire
- **Score**: Résultat du match
- **Localisation**: Domicile ou Extérieur
- **Résultat**: Victoire, Défaite, Match Nul

### 📥 Export Multiformat
- **XLSX** (Excel)
- **CSV** (Valeurs séparées par des virgules)

## 🛠️ Stack Technique

| Composant | Technologie |
|-----------|------------|
| **Backend** | Flask 3.0.0 |
| **Python** | 3.11.9 |
| **Données** | pandas 2.1.3, openpyxl 3.1.5 |
| **Scraping** | requests 2.32.3, BeautifulSoup4 4.12.3 |
| **Features** | emoji 2.8.0 |
| **Serveur** | gunicorn 21.2.0 |
| **Déploiement** | Render.com |

## 📁 Structure du Projet

```
data-extractor/
├── 🔧 Configuration
│   ├── app.py                    # Point d'entrée Flask
│   ├── config.py                 # Configuration (dev/prod)
│   ├── requirements.txt           # Dépendances Python
│   ├── Procfile                   # Config Render
│   ├── runtime.txt                # Version Python (3.11.9)
│   ├── .gitignore                 # Fichiers ignorés
│   └── README.md                  # Cette documentation
│
├── 📦 Code Source (src/)
│   ├── __init__.py
│   ├── twitter/
│   │   ├── __init__.py
│   │   └── extractor.py           # Extraction features Twitter
│   └── caen/
│       ├── __init__.py
│       ├── extractor.py           # Wrapper extraction SM Caen
│       └── scraper.py             # Scraper site officiel
│
├── 🎨 Interface (templates/)
│   └── index.html                 # UI responsive (français)
│
└── 📂 Assets Statiques (static/)
    ├── css/
    │   └── style.css              # Styles (couleurs SM Caen)
    ├── js/
    │   └── main.js                # Fonctionnalités client
    └── images/
        ├── Logo_X.svg             # Logo Twitter
        └── Logo_SM_Caen.svg       # Logo SM Caen
```

## 🚀 Démarrage Local

### Prérequis
- Python 3.11+
- pip

### Installation

1. **Cloner le repository**
```bash
git clone https://github.com/yourusername/data-extractor.git
cd data-extractor
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Lancer l'application**
```bash
python app.py
```

5. **Accéder à l'application**
```
http://localhost:5000
```

## 🌐 Déploiement sur Render

### Étape 1: Préparer GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### Étape 2: Créer un Web Service sur Render
1. Accéder à [render.com](https://render.com)
2. Cliquer sur "New +" → "Web Service"
3. Connecter le repository GitHub
4. Configurer:
   - **Name**: `data-extractor` (ou autre)
   - **Language**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Ajouter variables si nécessaire

### Étape 3: Déployer
Cliquer sur "Deploy" et laisser Render faire son travail!

## 💡 Utilisation

### Extraction Twitter

1. **Télécharger** un fichier (CSV, JSON, XLSX, ou JS)
   - Formats Twitter:
     - **CSV**: Colonnes: `full_text`, `created_at`, `favorite_count`, `retweet_count`
     - **JSON**: Objets tweets avec structure standard
     - **XLSX**: Feuille avec tweets
     - **JS**: Format export natif Twitter (`window.YTD.tweets.part1 = [...]`)

2. **Sélectionner les features** à extraire (min 1)
   - Utiliser "Tout sélectionner" pour rapidement cocher/décocher

3. **Choisir le format** de sortie (XLSX ou CSV)

4. **Télécharger** les données traitées

### Extraction SM Caen

1. **Entrer la plage d'années**
   - Année début: 2012-2026
   - Année fin: 2013-2027 (doit être > année début)
   - Exemples: 2021→2022 = saison 2021-2022 uniquement

2. **Choisir le format** de sortie (XLSX ou CSV)

3. **Télécharger** les données réelles depuis le site officiel

## 🔌 Endpoints API

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/` | Page principale |
| POST | `/extract-twitter` | Extraction features Twitter |
| POST | `/extract-caen` | Extraction données SM Caen |

### Exemple requête (Twitter)
```bash
curl -X POST http://localhost:5000/extract-twitter \
  -F "file=@tweets.csv" \
  -F "features=content" \
  -F "features=date" \
  -F "output_format=xlsx"
```

## ⚙️ Configuration

### Fichiers de configuration
- **config.py**: Paramètres de l'application
  - Max upload: 500MB
  - Formats autorisés: `csv, xlsx, xls, json, js`

- **runtime.txt**: Spécifie Python 3.11.9 pour Render

### Variables d'environnement
```bash
DEBUG=False        # Mode développement (False en prod)
```

## ✨ Caractéristiques Techniques

### Traitement de données
✅ Extraction intelligente de colonnes (détection automatique)
✅ Parsing Twitter format (Sat Oct 01 18:01:20 +0000 2016 → YYYY-MM-DD HH:MM:SS)
✅ Extraction entités imbriquées (hashtags, mentions depuis JSON)
✅ Fallback regex si entités manquantes
✅ Gestion des valeurs vides/nulles

### Web scraping SM Caen
✅ Scrape le site officiel (smcaen.fr)
✅ Détection flexible du nom Caen (caen, malherbe, smc)
✅ Rate limiting (0.8s délai entre requêtes)
✅ Calcul automatique scores/résultats
✅ Gestion des matchs non joués

### Interface utilisateur
✅ Responsive (mobile, tablet, desktop)
✅ Couleurs SM Caen (bleu marine #003d5c, rouge #c41e3a, doré #D4AF37)
✅ Toggle "Tout sélectionner" pour features
✅ Chargement avec spinner animé
✅ Messages d'erreur clairs
✅ Entièrement en français

## 🧪 Tests

### Test local
```bash
python app.py
```

### Test production (Gunicorn)
```bash
gunicorn app:app
```

Puis faire une requête POST aux endpoints.

## 📊 Limites et Restrictions

- **Taille fichier**: Max 500MB
- **Format Twitter**: Doit contenir colonnes reconnaissables (full_text, created_at, etc.)
- **Format JS**: Doit respecter `window.YTD.tweets.partX = [...]`
- **SM Caen**: Scraping du site officiel uniquement
- **Rate limit**: 0.8s minimum entre requêtes SM Caen

## 🐛 Gestion d'erreurs

L'application détecte et gère:
- ✅ Fichiers corrompus
- ✅ Formats non supportés
- ✅ Colonnes manquantes
- ✅ Données invalides (dates mal formatées, etc.)
- ✅ Problèmes de scraping (site down, timeout)
- ✅ Erreurs d'export (permissions fichier, espace disque)

Messages d'erreur explicites en français dans la UI.

## 📈 Performance

- Traitement pandas optimisé (in-memory)
- Export XLSX sans fichier intermédiaire (BytesIO)
- Scraping avec délai configuré pour respecter les serveurs
- Streaming de réponse pour gros fichiers

## 🤝 Contribution

Les contributions sont bienvenues! Pour contribuer:

1. Fork le repository
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📝 License

MIT License - voir LICENSE pour détails

## 👤 Auteur

Créé pour extraction et analyse de données Twitter et SM Caen.

---

**Questions?** Ouvrir une issue sur GitHub.

**Prêt à déployer?** Suivez le guide [Déploiement sur Render](#-déploiement-sur-render) ci-dessus!
