# QA Sales Call Analyzer

Automated QA analysis tool for sales call recordings. Upload audio or paste transcripts, and get structured feedback on intro quality, objection handling, close technique, and documentation.

## Features

- **Audio Upload** - Supports .mp3, .wav, .m4a, .ogg formats
- **Transcript Paste** - Analyze text transcripts directly
- **Qualifiers Input** - Add KDMs, timeline, disqualifiers for context
- **Structured Analysis** - Introduction, Relevant Topics, Close, Objection Handling, Opportunity, Documentation
- **History** - View past 50 analyses with full results
- **Edit & Re-analyze** - Modify results and reprocess with Gemini
- **Copy to Clipboard** - One-click copy of analysis results
- **Google Sheets Storage** - All results saved automatically

## Tech Stack

- **Framework:** [FastHTML](https://fastht.ml)
- **AI:** Gemini 2.0 Flash
- **Storage:** Google Sheets
- **Hosting:** Render (free tier)

## Hosting on Render (Free)

This app is designed to run on [Render's free tier](https://render.com). It's completely free and perfect for small tools like this.

### Cold Starts

Render's free tier has one catch: **your app sleeps after 15 minutes of inactivity**. When someone visits after it's asleep, there's a "cold start" delay of 30-60 seconds while the server spins back up.

To prevent this, we use a cron job to ping the app every 5 minutes and keep it awake.

### Deploy to Render

1. Push code to GitHub
2. Go to [Render](https://render.com) and connect your GitHub repo
3. Create a new **Web Service**
4. Configure:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `python main.py`
5. Add environment variables (see [Environment Variables](#environment-variables))
6. Deploy

### Keep-Alive with Cron

Use [cron-job.org](https://cron-job.org) (free) to ping your app and prevent cold starts:

1. Create a free account at [cron-job.org](https://console.cron-job.org/signup)
2. Create a new cron job:
   - **URL:** `https://your-app.onrender.com/health`
   - **Schedule:** Every 5 minutes
   - **Timezone:** Your preference

For specific hours only (e.g., Manila working hours 10 PM - 10 AM):
```
*/5 22-23,0-10 * * *
```

This keeps your app warm during work hours and lets it sleep overnight to save resources.

## Local Development (Optional)

If you want to run locally instead of Render:

### 1. Clone and Install

```bash
git clone https://github.com/DadiiLon/qa-calls-gemini.git
cd qa-calls-gemini
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create .env File

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### 3. Run

```bash
python main.py
```

Visit `http://localhost:5001`

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SESSION_SECRET` | Yes | 64-char hex for session encryption |
| `GOOGLE_API_KEY` | Yes | Gemini API key from AI Studio |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Yes | Service account JSON (single line) |
| `QA_PROMPT` | Yes | Your QA scorecard/analysis prompt |
| `PORT` | No | Server port (default: 5001) |

Generate session secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Setup: API Keys & Google Sheets

### Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy the key

### Set Up Google Sheets Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable the **Google Sheets API**
4. Go to **APIs & Services > Credentials**
5. Click **Create Credentials > Service Account**
6. Name it (e.g., `qa-sheets-writer`)
7. Click **Done**, then click the service account email
8. Go to **Keys > Add Key > Create new key > JSON**
9. Download the JSON file

### Create Google Sheet

1. Create a new Google Sheet named exactly: `QA Results`
2. Add headers in row 1: `Timestamp | Filename | Full Result`
3. Share the sheet with the service account email (found in JSON under `client_email`)
4. Give **Editor** access

## Project Structure

```
├── main.py           # Routes and server
├── config.py         # CSS, env vars, QA prompt
├── components.py     # UI components
├── handlers/
│   ├── gemini.py     # Gemini API integration
│   └── sheets.py     # Google Sheets storage
├── requirements.txt
└── .env
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main app (requires auth) |
| `/login` | GET/POST | Login page |
| `/logout` | GET | End session |
| `/health` | GET | Health check (no auth) |
| `/process_call` | POST | Analyze audio/transcript |
| `/tab/history` | GET | Load history grid |
| `/result/{timestamp}` | GET | View specific result |
