# GCP NextGen Summit 2026 - Informational Web Application

This is a premium, modern, responsive 1-day technical conference informational website built for **GCP NextGen Summit 2026**. 
It showcases the conference schedule, talk details, speaker profiles, and provides real-time search, category filtering, and personal bookmarking capabilities.

## Technical Architecture

- **Backend**: Python 3.13+ and Flask. The server defines the data models, implements endpoints, and renders HTML templates using Jinja2.
- **Frontend**: Custom Vanilla HTML5, CSS3, and modern JavaScript (ES6+). Includes background glows, glassmorphism interfaces, interactive transitions, and responsive mobile-first grids.
- **Visuals**: Abstract conference hero background generated matching Google Cloud brand aesthetics (vibrant blue, red, yellow, green accents on dark slate).

---

## Getting Started & Local Setup

Follow these instructions to run the application on your machine:

### Prerequisites
- Python 3.12 or newer installed on your machine.
- Pip (Python Package Manager).

### 1. Clone or Open the Directory
Open your terminal (PowerShell, Command Prompt, or Bash) in the project root directory:
```bash
cd c:/Zgemini/conference-website
```

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies:

**On Windows (PowerShell):**
```powershell
python -m venv .venv
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
```

### 3. Activate the Virtual Environment

**On Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
.\.venv\Scripts\activate.bat
```

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies
Install Flask using the provided `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 5. Launch the Server
Run the Flask application:
```bash
python app.py
```
You will see output indicating that the server is running on `http://127.0.0.1:5000`.

### 6. Review the App
Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## Project Structure

```
conference-website/
├── .venv/                  # Python virtual environment (auto-created)
├── static/
│   ├── css/
│   │   └── styles.css      # Dark mode variables, glassmorphism, responsive styles
│   ├── js/
│   │   └── main.js        # Search, category filter, bookmark storage, modal triggers
│   └── images/
│       └── hero_banner.jpg # Generated Google Cloud themed banner background
├── templates/
│   └── index.html          # Semantic HTML structure, stats counter, overlays, modals
├── app.py                  # Flask server containing conference database & routing
├── requirements.txt        # Flask dependency specification
└── README.md               # Setup and development guide (this file)
```

---

## Modifying the Website

### 1. Adding/Editing Speakers
All speakers are stored in the `SPEAKERS` dictionary in [app.py](file:///c:/Zgemini/conference-website/app.py). Add a new key and profile:
```python
"new_speaker_id": {
    "first_name": "Alice",
    "last_name": "Smith",
    "title": "Cloud Dev Advocate",
    "company": "Google Cloud",
    "bio": "Alice is an expert in cloud migration architectures.",
    "linkedin": "https://www.linkedin.com/in/alicesmith"
}
```

### 2. Adding/Editing Talks
Talks are stored in the `TALKS` list in [app.py](file:///c:/Zgemini/conference-website/app.py). To add a talk:
```python
{
    "id": "T9",
    "time": "16:30 - 17:10",
    "title": "Unveiling Next-Gen Edge Infrastructure",
    "category": "Cloud Infrastructure, DevOps & Security",
    "category_id": 2,
    "description": "An introduction to GCP Anthos at the Edge and edge compute clusters.",
    "speakers": ["new_speaker_id"]
}
```
*Note: Ensure Category ID is set to `1` (Track 1: AI & Data) or `2` (Track 2: Infra & Security), or `0` for custom breaks.*

### 3. Adjusting Styling
Modify CSS variables inside [static/css/styles.css](file:///c:/Zgemini/conference-website/static/css/styles.css) to change colors, fonts, or glassmorphic blur intensity.
