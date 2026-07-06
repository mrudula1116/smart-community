# 🏛️ CommunityPulse AI

**CommunityPulse AI** is an AI-powered Decision Intelligence Platform designed to help communities, municipalities, and organizations manage civic issues, emergency alerts, and community wellbeing through intelligent automation and analytics.

The platform is inspired by government portals like India's Sachet Portal and Smart City Command Centers, but modernized with a premium Glassmorphism UI and powered by Google Gemini AI.

## 🌟 Key Features

*   **Command Dashboard:** Real-time metrics, interactive charts (Chart.js), and a scrolling emergency ticker.
*   **AI Complaint Analyzer:** Intelligent routing, sentiment analysis, and severity scoring for citizen complaints.
*   **Emergency Preparedness:** Issue alerts with AI-generated safety guidance (Do's and Don'ts).
*   **AI Chat Assistant:** Query community data in natural language (e.g., "Predict next week's complaint volume").
*   **Predictive Analytics:** Forecasting and trend identification.
*   **Reports & Impact:** Auto-generate markdown reports and track the success of social impact initiatives.

## 🛠️ Technology Stack

*   **Backend:** Python 3, Flask, SQLite (zero-config, auto-seeding)
*   **Frontend:** Vanilla JavaScript (SPA), HTML5, custom CSS (Dark Mode Glassmorphism)
*   **AI Engine:** Google Gemini API (with built-in intelligent demo fallback)

## 🚀 Getting Started

### Prerequisites

*   Python 3.8+
*   *(Optional)* A Google Gemini API Key. You can get one from [Google AI Studio](https://aistudio.google.com/).

### Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory:
    ```bash
    cd "c:\Users\Readers' Paradise\Documents\AI_INTELLIGENCE"
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # On Windows:
    python -m venv venv
    .\venv\Scripts\activate
    
    # On macOS/Linux:
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration:**
    *   Rename `.env.example` to `.env`.
    *   *(Optional)* Add your `GEMINI_API_KEY` to the `.env` file to enable live AI analysis. If you skip this, the app will run in a fully functional **Demo Mode** with simulated AI responses.

### Running the Application

1.  Start the Flask server from your terminal:
    ```bash
    python app.py
    ```

2.  Open your web browser and navigate to:
    ```
    http://localhost:5000
    ```

*Note: On the first run, the SQLite database will automatically initialize and populate itself with realistic seed data so you can test the dashboard immediately.*

## 📁 Project Structure

```
AI_INTELLIGENCE/
│
├── app.py                  # Main Flask application and API routes
├── config.py               # App configuration and environment loading
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
│
├── services/               # Backend logic
│   ├── ai_service.py       # Gemini API integration & Demo fallback
│   ├── analytics.py        # Data aggregation for charts
│   └── database.py         # SQLite CRUD operations and seed data
│
├── static/                 # Frontend assets
│   ├── css/styles.css      # Premium design system
│   └── js/app.js           # SPA routing, API calls, and UI logic
│
└── templates/
    └── index.html          # Main HTML template
```
