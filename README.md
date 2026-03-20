# Data Extractor

A professional web application to extract and export Twitter and SM Caen (football) data in multiple formats.

**French User Interface** | **Render Deployment Ready** | **No External Dependencies**

## 🎯 Features

### 🐦 Twitter Features Extractor
Parse Twitter data from multiple formats (CSV, JSON, XLSX, JS) and extracts 9 features:
- **Content**: Full tweet text
- **Date**: ISO format (YYYY-MM-DD HH:MM:SS)
- **Hashtags**: Extract from entities or text
- **Mentions**: Mentioned usernames
- **Favorites**: Like count
- **Retweets**: Retweet count
- **Media**: Media presence detection
- **Mention Count**: Number of mentions
- **Emojis**: Emoji extraction

### ⚽ SM Caen Extractor
Scrapes real data from SM Caen official website and exports:
- **Season**: Season year(s)
- **Date & Time**: Temporal information
- **Competition**: Match type
- **Teams**: Home, Away, Opponent
- **Score**: Match result
- **Location**: Home or Away
- **Result**: Win, Loss, Draw

### 📥 Multi-format Export
- **XLSX** (Excel)
- **CSV** (Comma-separated values)

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask 3.0.0 |
| **Python** | 3.11.9 |
| **Data** | pandas 2.1.3, openpyxl 3.1.5 |
| **Web Scraping** | requests 2.32.3, BeautifulSoup4 4.12.3 |
| **Features** | emoji 2.8.0 |
| **Server** | gunicorn 21.2.0 |
| **Deployment** | Render.com |

## 📁 Project Structure

```
data-extractor/
├── 🔧 Configuration
│   ├── app.py                    # Flask entry point
│   ├── config.py                 # Configuration (dev/prod)
│   ├── requirements.txt           # Python dependencies
│   ├── Procfile                   # Render config
│   ├── runtime.txt                # Python version (3.11.9)
│   ├── .gitignore                 # Ignored files
│   └── README.md                  # This documentation
│
├── 📦 Source Code (src/)
│   ├── __init__.py
│   ├── twitter/
│   │   ├── __init__.py
│   │   └── extractor.py           # Twitter feature extraction
│   └── caen/
│       ├── __init__.py
│       ├── extractor.py           # SM Caen extraction wrapper
│       └── scraper.py             # Official website scraper
│
├── 🎨 Interface (templates/)
│   └── index.html                 # UI responsive (French)
│
└── 📂 Static Assets (static/)
    ├── css/
    │   └── style.css              # Styles (SM Caen branding)
    ├── js/
    │   └── main.js                # Client-side features
    └── images/
        ├── Logo_X.svg             # Twitter logo
        └── Logo_SM_Caen.svg       # SM Caen logo
```

## 🚀 Getting Started Locally

### Prerequisites
- Python 3.11+
- pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/data-extractor.git
cd data-extractor
```

2. **Create a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Access the application**
```
http://localhost:5000
```

## 🌐 Deployment on Render

### Step 1: Prepare GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 2: Create a Web Service on Render
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `data-extractor` (or your choice)
   - **Language**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Add variables if needed

### Step 3: Deploy
Click "Deploy" and let Render handle the rest!

## 💡 Usage

### Twitter Extraction

1. **Upload** a file (CSV, JSON, XLSX, or JS)
   - Twitter Formats:
     - **CSV**: Columns: `full_text`, `created_at`, `favorite_count`, `retweet_count`
     - **JSON**: Tweet objects with standard structure
     - **XLSX**: Sheet with tweets
     - **JS**: Native Twitter export format (`window.YTD.tweets.part1 = [...]`)

2. **Select features** to extract (minimum 1)
   - Use "Select All" to quickly check/uncheck all features

3. **Choose output format** (XLSX or CSV)

4. **Download** the processed data

### SM Caen Extraction

1. **Enter year range**
   - Start Year: 2012-2026
   - End Year: 2013-2027 (must be > start year)
   - Example: 2021→2022 = 2021-2022 season only

2. **Choose output format** (XLSX or CSV)

3. **Download** real data from the official website

## 🔌 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Main page |
| POST | `/extract-twitter` | Twitter feature extraction |
| POST | `/extract-caen` | SM Caen data extraction |

### Example Request (Twitter)
```bash
curl -X POST http://localhost:5000/extract-twitter \
  -F "file=@tweets.csv" \
  -F "features=content" \
  -F "features=date" \
  -F "output_format=xlsx"
```

## ⚙️ Configuration

### Configuration Files
- **config.py**: Application settings
  - Max upload: 150MB
  - Allowed formats: `csv, xlsx, xls, json, js`

- **runtime.txt**: Specifies Python 3.11.9 for Render

### Environment Variables
```bash
DEBUG=False        # Development mode (False in production)
```

## ✨ Technical Features

### Data Processing
✅ Intelligent column extraction (automatic detection)
✅ Twitter parsing (Sat Oct 01 18:01:20 +0000 2016 → YYYY-MM-DD HH:MM:SS)
✅ Nested entity extraction (hashtags, mentions from JSON)
✅ Regex fallback if entities missing
✅ Null/empty value handling

### SM Caen Web Scraping
✅ Scrapes official website (smcaen.fr)
✅ Flexible Caen name detection (caen, malherbe, smc)
✅ Rate limiting (0.8s delay between requests)
✅ Automatic score/result calculation
✅ Non-played match handling

### User Interface
✅ Responsive (mobile, tablet, desktop)
✅ SM Caen branding colors (navy #003d5c, red #c41e3a, gold #D4AF37)
✅ "Select All" toggle for features
✅ Animated loading spinner
✅ Clear error messages
✅ Fully in French language

## 🧪 Testing

### Local Test
```bash
python app.py
```

### Production Test (Gunicorn)
```bash
gunicorn app:app
```

Then make POST requests to the endpoints.

## 📊 Limitations and Restrictions

- **File Size**: Max 150MB
- **Twitter Format**: Must contain recognizable columns (full_text, created_at, etc.)
- **JS Format**: Must follow `window.YTD.tweets.partX = [...]`
- **SM Caen**: Official website scraping only
- **Rate Limit**: 0.8s minimum between SM Caen requests

## 🐛 Error Handling

The application detects and handles:
- ✅ Corrupted files
- ✅ Unsupported formats
- ✅ Missing columns
- ✅ Invalid data (malformed dates, etc.)
- ✅ Scraping issues (site unavailable, timeout)
- ✅ Export errors (file permissions, disk space)

Clear error messages in French in the UI.

## 📈 Performance

- Optimized pandas processing (in-memory)
- XLSX export without intermediate file (BytesIO)
- Scraping with configurable delay to respect servers
- Response streaming for large files

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see LICENSE for details

## 👤 Author

Created for Twitter and SM Caen data extraction and analysis.

---

**Questions?** Open an issue on GitHub.

**Ready to deploy?** Follow the [Deployment on Render](#-deployment-on-render) guide above!
