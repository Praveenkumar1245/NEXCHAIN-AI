# NexChain AI - Supply Chain Response Copilot

> **PS08 Disruption Response Engine**: LLM Entity Extraction + Deterministic Impact Calculations + Traceable Evidence Matrix

---

## 🚀 Quick Start Guide (How to Run from GitHub)

### 1. Prerequisites
- Python 3.9+ installed
- Git installed

### 2. Clone the Repository
```bash
git clone https://github.com/Praveenkumar1245/NEXCHAIN-AI.git
cd NEXCHAIN-AI
```

### 3. Set Up Virtual Environment (Recommended)
```bash
# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate

# On Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Configuration (Optional)

The application includes a **smart fallback engine** that guarantees full execution even without an API key. 

To use Google Gemini LLM extraction, set your API key:
```bash
# On Windows (PowerShell)
$env:GEMINI_API_KEY="your-gemini-api-key-here"

# On Linux/macOS
export GEMINI_API_KEY="your-gemini-api-key-here"
```

---

## ▶️ Running the Application

### Launch Web Server & Dashboard
```bash
python app.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:8000`**

### Run Backend Unit Tests
```bash
python test_backend.py
```

---

## ⚙️ Automated GitHub CI/CD

This repository includes a GitHub Actions workflow configured in `.github/workflows/ci.yml`. Every time you push code or open a pull request, GitHub will automatically execute `test_backend.py` to verify all supply chain calculations and data models.

---

## 📂 Project Architecture

```
.
├── app.py                 # FastAPI application server
├── test_backend.py        # Automated test suite
├── requirements.txt       # Python dependencies
├── src/
│   ├── data_loader.py     # CSV database loader
│   ├── gemini_client.py   # LLM extraction & fallback engine
│   ├── extractor.py       # Entity normalization & mapping
│   ├── impact_engine.py   # Pure Python inventory math engine
│   ├── ranking.py         # Customer order risk ranking
│   ├── recommender.py     # Mitigation option generator
│   └── evidence.py        # Auditable evidence tracing engine
├── frontend/              # Web user interface static files
└── data/                  # Sample supply chain datasets & disruption notices
```
