# QA Sales Call Analyzer

Automated QA analysis tool for sales call recordings. Upload audio or paste transcripts, and get structured feedback on intro quality, objection handling, close technique, and documentation.

## Features

- **Audio Upload** - Supports .mp3, .wav, .m4a, .ogg formats
- **Transcript Paste** - Analyze text transcripts directly
- **Qualifiers Input** - Add KDMs, timeline, disqualifiers for context
- **Structured Analysis** - Introduction, Relevant Topics, Close, Objection Handling, Opportunity, Documentation
- **History** - View past 100 analyses (newest first) with full results
- **Audio Playback** - Listen to recordings directly from history
- **Multi-word Search** - Search and highlight multiple keywords with different colors
- **Edit & Re-analyze** - Modify results and reprocess with Gemini
- **Copy to Clipboard** - One-click copy of analysis results
- **Turso Database** - Fast SQLite edge database for instant history loading
- **Google Cloud Storage** - Audio files stored persistently (optional)

## Tech Stack

| Tool | What It Does |
|------|--------------|
| <a href="https://fastht.ml" target="_blank">FastHTML</a> | Python web framework - lets you build websites using only Python (no JavaScript needed) |
| Gemini 2.0 Flash | Google's AI model that listens to audio and analyzes it |
| <a href="https://turso.tech" target="_blank">Turso</a> | SQLite edge database - fast, serverless database for storing analysis results |
| Google Cloud Storage | Stores audio files for playback in history (optional) |
| <a href="https://render.com" target="_blank">Render</a> | Free website hosting - puts your app on the internet |

---

## Hosting on Render (Free)

<a href="https://render.com" target="_blank">Render</a> is a free hosting service that runs your app on the internet. It's completely free for small projects like this.

### What Are Cold Starts?

Render's free tier has one catch: **your app goes to sleep after 15 minutes of no visitors**.

When someone visits your sleeping app:
1. Render wakes it up (takes 30-60 seconds)
2. The visitor sees a loading delay
3. After that, it's fast until it sleeps again

**Solution:** We use a "cron job" (automated ping) to visit your app every 5 minutes so it never falls asleep.

### Deploy to Render

1. Push your code to GitHub
2. Go to <a href="https://render.com" target="_blank">Render</a> and sign up (free)
3. Click **New > Web Service**
4. Connect your GitHub repo
5. Configure:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `python main.py`
6. Add your environment variables (see [Environment Variables](#environment-variables) below)
7. Click **Deploy**

Your app will be live at `https://your-app-name.onrender.com`

### Keep Your App Awake with Cron

A "cron job" is just an automated task that runs on a schedule. We'll use it to ping your app every 5 minutes.

1. Go to <a href="https://console.cron-job.org/signup" target="_blank">cron-job.org</a> (free)
2. Create an account
3. Click **Create Cronjob**
4. Set it up:
   - **URL:** `https://your-app-name.onrender.com/health`
   - **Schedule:** Every 5 minutes
   - **Timezone:** Asia/Manila (or your preference)
5. Save

Now your app stays awake during the hours you set.

### Understanding Cron Schedules (Optional)

By default, "Every 5 minutes" keeps your app awake 24/7. But you can customize when it runs using a cron expression.

A cron expression has 5 parts:
```
*     *     *     *     *
│     │     │     │     │
│     │     │     │     └── Day of week (0-6, Sunday=0)
│     │     │     └──────── Month (1-12)
│     │     └────────────── Day of month (1-31)
│     └──────────────────── Hour (0-23)
└────────────────────────── Minute (0-59)
```

**Example:** `*/5 22-23,0-10 * * *` means:
- `*/5` = Every 5 minutes
- `22-23,0-10` = During hours 22-23 (10-11 PM) AND 0-10 (12 AM - 10 AM)
- `* * *` = Every day, every month, every day of week

So this pings your app every 5 minutes from 10 PM to 10 AM Manila time - perfect for night shift work hours.

**Other examples:**
- `*/5 * * * *` = Every 5 minutes, 24/7
- `*/5 9-17 * * *` = Every 5 minutes, 9 AM to 5 PM only
- `*/5 9-17 * * 1-5` = Every 5 minutes, 9 AM to 5 PM, Monday to Friday only

---

## Local Development (Optional)

If you want to run this on your own computer instead of Render:

### 1. Clone and Install

```bash
# Download the code
git clone https://github.com/DadiiLon/qa-calls-gemini.git
cd qa-calls-gemini

# Create a virtual environment (keeps dependencies isolated)
python -m venv venv

# Activate it
source venv/bin/activate   # Mac/Linux
# venv\Scripts\activate    # Windows

# Install required packages
pip install -r requirements.txt
```

### 2. Create .env File

The `.env` file stores your secret keys. It's like a config file that never gets uploaded to GitHub.

```bash
cp .env.example .env
```

Then open `.env` and fill in your values (see below for how to get them).

### 3. Run

```bash
python main.py
```

Open your browser to `http://localhost:5001`

---

## Environment Variables

Environment variables are secret settings your app needs to run. On Render, you add these in the dashboard. Locally, they go in your `.env` file.

| Variable | Required | What It Is |
|----------|----------|------------|
| `SESSION_SECRET` | Yes | A random string that keeps user sessions secure. Generate one with the command below. |
| `GOOGLE_API_KEY` | Yes | Your Gemini AI key (lets you use Google's AI) |
| `TURSO_DATABASE_URL` | Yes | Your Turso database URL (e.g., `libsql://your-db.turso.io`) |
| `TURSO_AUTH_TOKEN` | Yes | Your Turso authentication token |
| `QA_PROMPT` | Yes | The instructions telling Gemini how to analyze calls |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | No | Credentials for Google Cloud Storage (for audio playback in history) |
| `GCS_BUCKET_NAME` | No | Your GCS bucket name (default: `qa-calls-audio`) |
| `PORT` | No | Which port to run on (default: 5001) |

### Generate a Session Secret

Run this in your terminal:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (a long random string) and use it as your `SESSION_SECRET`.

---

## Setup: API Keys & Database

### Step 1: Get Gemini API Key

This key lets your app use Google's AI to analyze calls.

1. Go to <a href="https://aistudio.google.com/apikey" target="_blank">Google AI Studio</a>
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key - this is your `GOOGLE_API_KEY`

### Step 2: Set Up Turso Database

Turso is a fast, serverless SQLite database that stores your analysis results.

1. Install the Turso CLI:
   ```bash
   curl -sSfL https://get.tur.so/install.sh | bash
   ```

2. Sign up and login:
   ```bash
   turso auth login
   ```

3. Create a database:
   ```bash
   turso db create qa-calls
   ```

4. Get your database URL:
   ```bash
   turso db show qa-calls --url
   ```
   Copy this - it's your `TURSO_DATABASE_URL`

5. Create an auth token:
   ```bash
   turso db tokens create qa-calls
   ```
   Copy this - it's your `TURSO_AUTH_TOKEN`

### Step 3: Set Up Google Cloud Storage (Optional - for audio playback)

If you want to replay audio recordings from history, set up GCS:

1. Go to <a href="https://console.cloud.google.com" target="_blank">Google Cloud Console</a>
2. Create a new project (or select existing)
3. Search for **Cloud Storage** and click **Create Bucket**
4. Name it (e.g., `qa-calls-audio`) and create it
5. Go to **APIs & Services > Credentials**
6. Click **Create Credentials > Service Account**
7. Name it something like `qa-audio-storage`
8. Click **Done**, then click on the service account
9. Go to **Keys** tab > **Add Key** > **Create new key** > **JSON**
10. Download the JSON file

Copy the entire JSON contents as your `GOOGLE_SERVICE_ACCOUNT_JSON`.

Then give the service account access to your bucket:
1. Go to your bucket in Cloud Storage
2. Click **Permissions** > **Grant Access**
3. Add the service account email with **Storage Object Admin** role

---

## Project Structure

```
├── main.py           # The main app - routes and server
├── config.py         # Settings - CSS styles, loads environment variables
├── components.py     # UI building blocks - buttons, cards, forms
├── handlers/
│   ├── gemini.py     # Talks to Gemini AI
│   ├── database.py   # Talks to Turso database
│   └── storage.py    # Handles audio file storage (GCS)
├── requirements.txt  # List of Python packages needed
└── .env              # Your secret keys (not uploaded to GitHub)
```

---

## API Endpoints

These are the URLs your app responds to:

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/` | GET | Main page - the upload form |
| `/health` | GET | Returns "ok" - used by cron to keep app awake |
| `/process_call` | POST | Analyzes an uploaded audio/transcript |
| `/tab/history` | GET | Shows past analyses |
| `/result/{timestamp}` | GET | Shows a specific past analysis |
