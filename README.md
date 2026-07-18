# StadiumPulse AI 🏟️

Smart Stadium Operations & Fan Assistant built for the **Google PromptWars (Hack2Skill) — Challenge 4: Smart Stadiums & Tournament Operations**.

> **Disclaimer:** This project uses a fictional venue ("Continental Park Stadium") built specifically for a hackathon submission. It is not affiliated with or endorsed by FIFA.

## 🔗 Important Links
* **GitHub Repository:** [Insert Github Link Here]
* **Live Deployment:** [Insert Deployment Link Here]
* **LinkedIn Post:** [Insert Linkedin Post Link Here]

## 🌟 Overview

StadiumPulse AI provides a unified backend and real-time operations engine for a smart stadium. It serves two main personas:
1. **Fan Assistant**: An AI chatbot (powered by Google Gemini) that helps fans navigate the stadium, find facilities, get real-time queue updates, and answer FAQs.
2. **Ops Dashboard**: A real-time monitoring view for stadium staff to track crowd density, gate queues, and stadium occupancy dynamically.

## 🛠️ Tech Stack

* **Frontend:** React, TypeScript, Vite, Vanilla CSS (Glassmorphism & Neon Design)
* **Backend:** FastAPI, Python, SQLite (aiosqlite)
* **AI Engine:** Google Gemini (Gemini 2.5 Flash Lite) with Automatic Function Calling
* **Real-time Data:** WebSockets for live crowd simulation

## 🚀 Key Features

* **AI Tool Calling:** The Fan Assistant interacts directly with the live database using Gemini Function Calling to give accurate, non-hallucinated answers about wait times and locations.
* **Prompt Injection Guard:** An input guard checks messages using deterministic AI models to prevent jailbreaks or out-of-context requests.
* **Live Crowd Simulator:** A background engine dynamically simulates crowd curves, advancing match time and updating queues every 5 seconds.

## 💻 Local Setup Instructions

### 1. Requirements
- Python 3.11+
- Node.js (v18+)
- Google Gemini API Key (get from [AI Studio](https://aistudio.google.com/))

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/R123456-123/stadium-pulse-ai.git
cd stadium-pulse-ai/backend

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # On Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and set your GEMINI_API_KEY

# Seed the initial database
python -m app.seed.seed_data

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
Open a new terminal window:
```bash
cd stadium-pulse-ai/frontend

# Install dependencies
npm install

# Start the React development server
npm run dev
```

The web application will be available at `http://localhost:5173`. Interactive API documentation can be accessed at `http://localhost:8000/docs`.
