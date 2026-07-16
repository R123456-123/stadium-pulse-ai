# StadiumPulse AI 🏟️

Smart Stadium Operations & Fan Assistant built for the **Google PromptWars (Hack2Skill) — Challenge 4: Smart Stadiums & Tournament Operations**.

> **Disclaimer:** This project uses a fictional venue ("Continental Park Stadium") built specifically for a hackathon submission. It is not affiliated with or endorsed by FIFA.

## Overview

StadiumPulse AI provides a unified backend and real-time operations engine for a smart stadium. It serves two main personas:
1. **Fan Assistant** (Upcoming): An AI chatbot that helps fans navigate the stadium, find facilities, and get real-time queue updates.
2. **Ops Dashboard** (Upcoming): A real-time monitoring view for stadium staff to track crowd density, gate queues, and sustainability metrics.

## What's Built So Far (Backend)

The backend is built with **FastAPI** and uses **SQLite** for the database. 
- **Core API Layer**: REST endpoints for querying zones, gates, facilities, transport options, and FAQs.
- **Crowd Simulator**: A background engine that simulates a realistic match-day crowd curve, updating occupancy and wait times every 5 seconds.
- **Real-Time Data**: A WebSocket endpoint (`/api/v1/ws/crowd`) that pushes live crowd density, queue times, and sustainability estimates to connected clients.
- **Sustainability Tracking**: Computes live energy consumption and waste generation estimates based on active zone occupancy.

## Setup Instructions

### 1. Requirements
- Python 3.11+
- Google Gemini API Key

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/R123456-123/stadium-pulse-ai.git
cd stadium-pulse-ai/backend

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # On Windows

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio ruff mypy
```

### 3. Configuration
Copy the environment template and add your Gemini API key:
```bash
copy .env.example .env
```
Edit `.env` and set your `GEMINI_API_KEY`.

### 4. Running the Application
Seed the initial database with demo stadium data:
```bash
python -m app.seed.seed_data
```

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. 
Interactive API documentation can be accessed at `http://localhost:8000/docs`.
