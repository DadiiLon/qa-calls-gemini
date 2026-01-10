from fasthtml.common import *
from google import genai
from google.genai import types
from starlette.responses import RedirectResponse
from datetime import datetime
import gspread
import json
import os

# ============ CONFIG ============
SESSION_PASSWORD = os.environ.get("SESSION_PASSWORD", "changeme")
SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-secret-change-in-prod")

# ============ AUTH SETUP ============
login_redir = RedirectResponse('/login', status_code=303)

def auth_before(req, sess):
    auth = req.scope['auth'] = sess.get('auth', None)
    if not auth:
        return login_redir

beforeware = Beforeware(
    auth_before,
    skip=[r'/favicon\.ico', r'/static/.*', '/login', '/health']
)

app, rt = fast_app(
    before=beforeware,
    secret_key=SESSION_SECRET,
    hdrs=(
        Script(src="https://unpkg.com/htmx.org@1.9.10"),
    )
)

# ============ GEMINI CLIENT ============
gemini_client = genai.Client()  # Uses GOOGLE_API_KEY env var

# ============ GOOGLE SHEETS ============
def get_sheets_client():
    creds = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    gc = gspread.service_account_from_dict(creds)
    return gc.open("QA Results").sheet1

# ============ HEALTH CHECK (for uptime monitoring) ============
@rt("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# ============ ROUTES ============

@rt("/login")
def get_login():
    return Titled("QA Tool - Login",
        Form(method="post")(
            Input(name="password", type="password", placeholder="Password", required=True),
            Button("Login")
        )
    )

@rt("/login", methods=["POST"])
async def post_login(req, sess):
    form = await req.form()
    password = form.get("password", "")
    print(f"DEBUG: entered='{password}' expected='{SESSION_PASSWORD}'")
    if password == SESSION_PASSWORD:
        sess['auth'] = "authenticated"
        return RedirectResponse('/', status_code=303)
    return Titled("QA Tool - Login",
        P("Invalid password", style="color: red"),
        Form(method="post")(
            Input(name="password", type="password", placeholder="Password", required=True),
            Button("Login")
        )
    )

@rt("/logout")
def logout(sess):
    sess['auth'] = None
    return RedirectResponse('/login', status_code=303)

@rt("/")
def home(auth):
    return Titled("QA Call Analyzer",
        Form(
            hx_post="/process_audio",
            hx_target="#result-box",
            hx_swap="innerHTML",
            enctype="multipart/form-data"
        )(
            Input(type="file", name="audio", accept="audio/*", required=True),
            Button("Analyze Call"),
        ),
        Div(id="result-box", style="margin-top: 20px; white-space: pre-wrap;")
    )

@rt("/process_audio", methods=["POST"])
async def process_audio(audio: UploadFile):
    try:
        # Read audio bytes
        audio_bytes = await audio.read()

        # Determine MIME type
        ext = audio.filename.lower().split('.')[-1]
        mime_map = {'mp3': 'audio/mp3', 'wav': 'audio/wav', 'ogg': 'audio/ogg', 'm4a': 'audio/mp4'}
        mime_type = mime_map.get(ext, 'audio/mpeg')

        # Call Gemini with QA prompt
        response = gemini_client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[
                QA_PROMPT,
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
            ]
        )

        result_text = response.text

        # Save to Google Sheets
        try:
            sheet = get_sheets_client()
            sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                audio.filename,
                result_text[:500],  # Summary (first 500 chars)
                result_text         # Full response
            ])
        except Exception as e:
            result_text += f"\n\n⚠️ Failed to save to Sheets: {e}"

        return Div(
            H3("Analysis Complete"),
            Pre(result_text)
        )

    except Exception as e:
        return Div(
            P(f"Error: {str(e)}", style="color: red")
        )

# ============ QA PROMPT ============
# Load from environment variable (keeps scorecard private)
QA_PROMPT = os.environ.get("QA_PROMPT", """You are a Quality Assurance Analyst responsible for evaluating SALES call recordings for appointment setting.

Analyze this audio recording and provide a structured analysis based on the categories below.
All required elements must be verified and supported by transcript evidence.

⚠️ CRITICAL: Pay special attention to tentative meetings and accurately identify KDM vs Influencers.

---

## MANDATORY CHECKS (apply to ALL calls):
- Rep stated the call is being recorded
- Rep explicitly said "accept" when confirming meeting (NO substitutes allowed - must use exact word "accept")

---

## 1. INTRODUCTION

Mark ONLY ONE section below (Non-Follow Up OR Follow-Up):

### A. NON-FOLLOW UP CALL
- RLM Stated: [Done / Not Done / N/A]
- Value Differentiator: [Done / Not Done / N/A]
- Objection Takeaway: [Done / Not Done / N/A]
- 1st Open-Ended Question: [Done / Not Done / N/A]

### B. FOLLOW-UP CALL (any succeeding call after a pitch or contact with the KDM)
- RLM Stated: [Done / Not Done / N/A]
- Recap (previous conversation summarized): [Done / Not Done / N/A]
- Reintroduce with Value: [Done / Not Done / N/A]
- Recommend / Reopen: [Done / Not Done / N/A]

---

## 2. RELEVANT TOPICS

⚠️ Questions MUST be open-ended.

- Asked about services/capabilities: [Done / Not Done / N/A]
- Asked about most consistent issue: [Done / Not Done / N/A]

---

## 3. CLOSE

- Assumed close with 2 suggested dates/times: [Done / Not Done / N/A]
- Attempted to schedule within 5 business days (based on grading date): [Done / Not Done / N/A]
- Meeting Date & Time Confirmed: [Done / Not Done / N/A]
- Meeting Type (In-Person / Virtual / Phone): [Done / Not Done / N/A]

---

## 4. OBJECTION HANDLING (score only when applicable)

- Used "Feel, Felt, Found": [Done / Not Done / N/A]
- Used "Worst Case Scenario": [Done / Not Done / N/A]
- Count number of objections: [X objections]

---

## 5. OPPORTUNITY QUALITY

- Followed client scheduling preferences: [Done / Not Done / N/A]
- Asked Golden Question verbatim or similar version:
  "If you see value after this meeting, what does the typical timeline and decision-making process look like?"
  [Done / Not Done / N/A]
- Asked about contract end date / reevaluation time: [Done / Not Done / N/A]

---

## 6. DOCUMENTATION

- Prospect explicitly asked to "accept" invite (exact wording required): [Done / Not Done / N/A]

Contact Info Verified:
- First & Last Name: [Done / Not Done]
- Phone Number: [Done / Not Done]
- Email Address: [Done / Not Done]
- Complete Address: [Done / Not Done]
- Position/Job Title: [Done / Not Done]

---

## 7. APPOINTMENT QUALIFICATION

- Qualified appointment? [Yes / No]
- If No, explain reason (ex: below size threshold, public sector, not building owner, etc.)
- List all Qualifiers checked: [...]
- List all Disqualifiers checked: [...]
- Confirm specific date/time of appointment: [...]
- Meeting type: [In-person / Virtual / Phone]

---

## 8. DECISION MAKER ASSESSMENT

- Prospect title and role identified: [...]
- Classification: [KDM / Influencer]

---

## 9. MEETING PURPOSE & TIMELINE

- Agenda stated by rep: [Done / Not Done]
- Immediate need or interest mentioned: [Yes / No + details]

Project timeline classified as:
- [0-6 months / 6-12 months / 12+ months]

---

## 10. DARTS SCORE

Provide score for each category with justification:

**D = Desire to Meet:**
- 2 = No Objection
- 1 = Two or less objections
- 0 = Three plus objections
Score: [X] – Reason: [...]

**A = Authority:**
- 2 = Final KDM
- 1 = Influencer
- 0 = Neither
Score: [X] – Reason: [...]

**R = Revenue Opportunity:**
- 3 = Immediate Need
- 2 = Interest
- 1 = Willing to Meet
- 0 = No Interest
Score: [X] – Reason: [...]

**T = Timeliness:**
- 2 = 0-6 months
- 1 = 6-12 months
- 0 = 12+ months
Score: [X] – Reason: [...]

**S = Size:**
- 2 = Huge Opportunity
- 1 = Qualified
- 0 = Not Qualified
Score: [X] – Reason: [...]

**TOTAL DARTS SCORE: [X/11]**

---

## 11. FEEDBACK (REQUIRED)

Follow this exact format:

**Intro:**
[Specific feedback on RLM, Value Differentiator, Objection Takeaway, Open-Ended Question]

**Relevant Topics:**
[Feedback on services/capabilities question and consistent issues question - note if open-ended]

**Close:**
[Feedback on assumptive close with two dates, within 5 business days check]

**Objection Handling:**
[Feedback on Feel/Felt/Found and Worst Case Scenario usage]

**Opportunity:**
[Feedback on Golden Question, contract end date, scheduling preferences]

**Documentation:**
Email: [Done / Not confirmed]
Phone: [Done / Not confirmed]
Title: [Done / Not confirmed]
Address: [Done / Not confirmed]

---

Now analyze the audio recording:""")

# ============ START SERVER ============
if __name__ == '__main__':
    serve(port=int(os.getenv("PORT", 5001)))
