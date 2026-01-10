# QA Sales Call Analyzer

Analyzes sales call recordings using Gemini AI. Evaluates intro quality, close technique, objection handling, documentation, and calculates DARTS score.

## Tech Stack

- **Framework:** FastHTML
- **AI:** Gemini 1.5 Flash
- **Storage:** Google Sheets
- **Hosting:** Render (free tier)

## Local Development

```bash
# Set environment variables
export SESSION_PASSWORD=yourpassword
export SESSION_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
export GOOGLE_API_KEY=your-gemini-api-key
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'

# Run
python main.py
```

Visit `http://localhost:5001`

## Environment Variables

| Variable                      | Description                                                         |
| ----------------------------- | ------------------------------------------------------------------- |
| `SESSION_PASSWORD`            | Login password                                                      |
| `SESSION_SECRET`              | 64-char hex for session encryption                                  |
| `GOOGLE_API_KEY`              | Gemini API key from [AI Studio](https://aistudio.google.com/apikey) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Service account JSON for Google Sheets                              |

## Render Deployment

1. Connect GitHub repo
2. Set environment variables above
3. Build command: `pip install -r requirements.txt`
4. Start command: `python main.py`

## Keep-Alive (Prevent Cold Boots)

Use [cron-job.org](https://cron-job.org) to ping `/health` endpoint:

- Expression: `*/5 14-23,0-2 * * *` (10 PM - 10 AM Manila time)
- Timezone: UTC
