# Project Overview Report: QA Sales Call Analyzer

## What Is This Project?

**QA Sales Call Analyzer** is an automated Quality Assurance tool for evaluating sales call recordings. Users can upload audio recordings or paste transcripts, and the application uses **Google's Gemini 2.0 Flash AI** to analyze them against a customizable QA scorecard. Results are stored in Google Sheets and viewable in a history dashboard.

**Target Users:** Sales QA teams, sales managers, and training organizations that need to evaluate sales call quality at scale.

---

## Directory Structure

```
/home/user/qa-calls-gemini/
├── main.py                    # FastHTML server + route handlers (232 lines)
├── config.py                  # Configuration, CSS styles, env vars (469 lines)
├── components.py              # Reusable UI components (270 lines)
├── handlers/
│   ├── __init__.py           # Exports all handlers
│   ├── gemini.py             # Gemini AI integration (116 lines)
│   └── sheets.py             # Google Sheets integration (62 lines)
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── README.md                 # User documentation
└── CHANGELOG.md              # Version history
```

---

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | FastHTML web server with all routes (`/`, `/process_call`, `/tab/history`, `/result/{timestamp}`, `/edit_form`, `/reanalyze`, `/health`) |
| `config.py` | Environment variables, session secret, QA_PROMPT, and 465 lines of dark theme CSS |
| `components.py` | UI components: `render_process_tab()`, `render_results_card()`, `render_history_card()`, `render_edit_form()`, `render_result_detail()` |
| `handlers/gemini.py` | AI integration: `analyze_audio()`, `analyze_transcript()`, `reanalyze_text()`, `extract_darts_score()`, mock fallback |
| `handlers/sheets.py` | Google Sheets: `save_result()`, `get_history()`, `find_record_by_timestamp()`, in-memory fallback |

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Web Framework** | FastHTML (Python-only, generates HTML) |
| **AI Model** | Gemini 2.0 Flash (audio transcription + analysis) |
| **Frontend** | HTMX 1.9.10 (dynamic updates), Dark theme CSS |
| **Storage** | Google Sheets API v4 (via gspread) |
| **Server** | Uvicorn (ASGI, async support) |
| **Auth** | google-auth (service account credentials) |
| **Deployment** | Render.com (free tier) |

---

## Application Flow

```
1. User visits /
   └─ Renders Process tab (upload form) + History tab

2. POST /process_call
   ├─ Audio: Sends bytes to Gemini → transcribes + analyzes
   ├─ Transcript: Sends text to Gemini → analyzes
   ├─ Extracts DARTS score [X/11] from result
   ├─ Saves to Google Sheets (Timestamp, Filename, Result)
   ├─ Stores in session for edit feature
   └─ Returns results card with markdown-rendered output

3. GET /tab/history
   ├─ Fetches all records from Sheets (newest first, max 50)
   └─ Renders clickable history cards

4. GET /edit_form → POST /reanalyze
   ├─ User edits previous result
   ├─ Sends to Gemini for re-analysis
   └─ Saves as new record ("Re-analyzed" filename)
```

---

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `SESSION_SECRET` | Yes | Session encryption key |
| `GOOGLE_API_KEY` | Yes | Gemini API access |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Yes | Sheets credentials (single line JSON) |
| `QA_PROMPT` | Yes | Scorecard evaluation instructions |
| `PORT` | No | Server port (default: 5001) |

---

## Features

- **Audio upload** - Supports mp3, wav, m4a, ogg
- **Transcript paste** - Direct text analysis
- **Qualifiers input** - Add context (KDMs, timeline, etc.)
- **DARTS score extraction** - Parses `[X/11]` from results
- **Edit & Re-analyze** - Modify and re-process results
- **History dashboard** - View past 50 analyses
- **Copy to clipboard** - One-click result copying
- **Mock mode** - Works without API keys for testing
- **Health endpoint** - `/health` for uptime monitoring

---

## Deployment

### Local Development

```bash
git clone https://github.com/DadiiLon/qa-calls-gemini.git
cd qa-calls-gemini
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
python main.py  # Runs on http://localhost:5001
```

### Render.com Production

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `python main.py`
- **Keepalive:** Set up cron job to ping `/health` every 5 minutes

---

## Dependencies

```
python-fasthtml   # Web framework
python-dotenv     # Environment variable loading
google-genai      # Gemini AI API client
uvicorn           # ASGI server
gspread           # Google Sheets API client
google-auth       # Google authentication
pytz              # Timezone handling
markdown          # Convert markdown to HTML
```

---

## Testing Status

- **No automated tests** in repository
- **Mock mode** enables UI testing without API costs
- **Manual browser testing** during development

---

## Architecture Highlights

### Graceful Fallbacks
- When `GOOGLE_API_KEY` is missing → uses mock AI analysis
- When `GOOGLE_SERVICE_ACCOUNT_JSON` is missing → uses in-memory storage

### Session Management
- Stores `last_result` and `last_filename` for edit feature
- Encrypted with `SESSION_SECRET`

### Error Handling
- Try/catch blocks on all routes
- User-friendly error cards instead of 500 errors

---

## Summary

A **lean, focused Python web application** (~1,150 lines total) that:

- Uses FastHTML for Python-first web development
- Leverages Gemini 2.0 Flash for AI analysis
- Stores results in Google Sheets (free cloud DB)
- Provides a polished dark-theme SPA experience
- Gracefully falls back to mock mode when APIs unavailable
- Deploys easily to Render.com's free tier

**Strengths:**
- Simple, modular architecture
- Works without internet APIs (mock mode)
- Minimal dependencies
- Dark UI with good UX
- Session-based edit feature
- Cloud storage integration

**Key Files to Understand:**
1. `main.py` - Route logic and request handling
2. `handlers/gemini.py` - AI integration
3. `handlers/sheets.py` - Data persistence
4. `components.py` - UI rendering
5. `config.py` - Styling and settings
