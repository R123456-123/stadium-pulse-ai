# StadiumPulse AI 🏟️

Smart Stadium Operations & Fan Assistant built for the **Google PromptWars (Hack2Skill)**.

## 🔗 Important Links
* **GitHub Repository:** https://github.com/R123456-123/stadium-pulse-ai
* **Live Deployment:** https://stadium-pulse-ai-blush.vercel.app/
* **LinkedIn Post:** [LinkedIn Post](https://www.linkedin.com/posts/rishiraj-tanwar_googlepromptwars-hack2skill-googlegemini-share-7484251326298669056-bXJt)

## 🌟 What We Built
StadiumPulse AI is a real-time smart stadium platform that serves two main purposes:
1. **Fan Assistant**: An AI chatbot that helps fans navigate the stadium, find restrooms, get live gate wait times, and read stadium policies.
2. **Operations Dashboard**: A live command center for stadium staff to monitor crowd density and get AI-generated safety alerts when zones get too crowded.

## 🛠️ What We Used
* **Frontend:** React, TypeScript, Vite
* **Backend:** FastAPI, Python, SQLite, WebSockets
* **AI & Logic:** Google Gemini API (`gemini-3.1-flash-lite`)

## 🧠 How We Used Google Services (Gemini)
Google Gemini is the core brain of our application. We used it in two powerful ways:
1. **Automated Function Calling (AFC):** Instead of hallucinating answers, our Fan Assistant uses Gemini's Function Calling feature. When a fan asks "Where is the restroom?", Gemini automatically triggers our Python backend functions to query the live SQLite database and returns real, accurate locations.
2. **Built-in Prompt Guard:** We integrated strict system instructions directly into our Gemini prompt to gracefully handle off-topic questions and prompt injections, keeping the bot completely focused on stadium operations.

## 🚀 Important Deployment Instructions
If you are deploying this project, you must set these environment variables!

### Backend (e.g. Render)
Ensure these environment variables are set on your backend host:
* `GEMINI_API_KEY` = Your Google AI Studio Key
* `GEMINI_MODEL` = `gemini-3.1-flash-lite`

### Frontend (Vercel)
Our frontend relies on environment variables to know where the backend is. In your Vercel project settings, you **must** add:
* `VITE_API_URL` = `https://stadium-pulse-ai-t33k.onrender.com`
* `VITE_WS_URL` = `wss://stadium-pulse-ai-t33k.onrender.com/api/v1/ws/crowd`

**Important:** After adding these on Vercel, you must trigger a **Redeploy** so the frontend can successfully connect to the AI and live data!

## 💻 Local Testing
1. Navigate to the `backend/` folder. 
2. Add your `.env` file with your `GEMINI_API_KEY`.
3. Run `pip install -r requirements.txt` and start the server with `uvicorn app.main:app --reload`.
4. In a separate terminal, navigate to the `frontend/` folder. 
5. Run `npm install` and start the UI with `npm run dev`.
