from fasthtml.common import *
from google import genai
from google.genai import types
from starlette.responses import RedirectResponse
from datetime import datetime
import gspread
import json
import os
import re

# ============ CONFIG ============
SESSION_PASSWORD = os.environ.get("SESSION_PASSWORD", "changeme")
SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-secret-change-in-prod")

# ============ CSS STYLES ============
CSS = """
:root {
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --bg: #f3f4f6;
    --card-bg: #ffffff;
    --border: #e5e7eb;
    --text: #1f2937;
    --text-muted: #6b7280;
    --success: #10b981;
    --error: #ef4444;
    --radius: 8px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    min-height: 100vh;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    padding: 24px 16px;
}

h1 {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 24px;
    color: var(--text);
}

/* Tabs */
.tabs {
    display: flex;
    gap: 4px;
    border-bottom: 2px solid var(--border);
    margin-bottom: 24px;
}

.tab {
    padding: 12px 24px;
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
    cursor: pointer;
    font-size: 15px;
    font-weight: 500;
    color: var(--text-muted);
    transition: all 0.15s;
}

.tab:hover { color: var(--primary); }
.tab.active {
    color: var(--primary);
    border-bottom-color: var(--primary);
}

/* Cards */
.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.card-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-header h2, .card-header h3 {
    font-size: 18px;
    font-weight: 600;
    margin: 0;
}

.card-body { padding: 20px; }
.card-body.scrollable {
    max-height: 500px;
    overflow-y: auto;
}

.card-footer {
    padding: 16px 20px;
    border-top: 1px solid var(--border);
    background: #fafafa;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

/* Form elements */
input[type="file"],
input[type="text"],
input[type="password"],
textarea {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    font-size: 14px;
    font-family: inherit;
    margin-bottom: 12px;
}

textarea {
    min-height: 200px;
    resize: vertical;
    font-family: monospace;
}

button, .btn {
    padding: 10px 20px;
    background: var(--primary);
    color: white;
    border: none;
    border-radius: var(--radius);
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: background 0.15s;
}

button:hover, .btn:hover { background: var(--primary-hover); }

.btn-secondary {
    background: #6b7280;
}
.btn-secondary:hover { background: #4b5563; }

/* DARTS badge */
.darts-badge {
    display: inline-block;
    padding: 6px 14px;
    background: var(--success);
    color: white;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
}

/* Metadata */
.metadata {
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
    font-size: 14px;
}
.metadata p { margin: 4px 0; }
.metadata strong { color: var(--text); }

/* Result text */
.result-text {
    white-space: pre-wrap;
    font-family: monospace;
    font-size: 13px;
    line-height: 1.5;
    background: #f9fafb;
    padding: 16px;
    border-radius: var(--radius);
    border: 1px solid var(--border);
}

/* History grid */
.history-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
}

.history-item { cursor: pointer; transition: box-shadow 0.15s; }
.history-item:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

.history-item .filename {
    font-weight: 600;
    font-size: 14px;
    word-break: break-all;
}

.history-item .timestamp {
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 8px;
}

.history-item .summary {
    font-size: 13px;
    color: var(--text-muted);
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Loading spinner */
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator { display: block; }
.htmx-request.htmx-indicator { display: block; }

.spinner-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(255,255,255,0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.spinner {
    width: 48px;
    height: 48px;
    border: 4px solid var(--border);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Error state */
.error-text { color: var(--error); }

/* Empty state */
.empty-state {
    text-align: center;
    padding: 48px 24px;
    color: var(--text-muted);
}

/* Info text */
.info-text {
    font-size: 13px;
    color: var(--text-muted);
}

/* Copy button */
.btn-copy {
    background: #6b7280;
    padding: 6px 12px;
    font-size: 13px;
}
.btn-copy:hover { background: #4b5563; }
.btn-copy.copied {
    background: var(--success);
}

/* Toast notification */
.toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: var(--success);
    color: white;
    padding: 12px 20px;
    border-radius: var(--radius);
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s ease;
    z-index: 1000;
}
.toast.show {
    opacity: 1;
    transform: translateY(0);
}

/* Processing card */
.processing-text {
    text-align: center;
    padding: 40px 20px;
}
.processing-text p {
    margin-top: 16px;
    font-size: 15px;
    color: var(--text-muted);
}
.processing-text .spinner {
    margin: 0 auto;
}

/* Mobile responsive */
@media (max-width: 640px) {
    .container { padding: 16px 12px; }
    h1 { font-size: 20px; }
    .tabs { gap: 0; }
    .tab { padding: 10px 16px; font-size: 14px; }
    .card-header, .card-body, .card-footer { padding: 14px 16px; }
    .card-footer { flex-direction: column; }
    .card-footer button { width: 100%; }
    .history-grid { grid-template-columns: 1fr; }
    .darts-badge { font-size: 12px; padding: 4px 10px; }
}
"""

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
        Style(CSS),
    )
)

# ============ GEMINI CLIENT ============
try:
    gemini_client = genai.Client()  # Uses GOOGLE_API_KEY env var
except ValueError:
    gemini_client = None  # Mock mode for local testing

# ============ GOOGLE SHEETS ============
mock_sheet_data = []  # In-memory storage for mock mode

def get_sheets_client():
    if gemini_client is None:
        return None  # Mock mode
    creds = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    gc = gspread.service_account_from_dict(creds)
    return gc.open("QA Results").sheet1

# ============ UTILITIES ============
def extract_darts_score(text):
    """Extract DARTS score from result text"""
    match = re.search(r'TOTAL DARTS SCORE:\s*\[?(\d+)/11\]?', text)
    return match.group(1) if match else "N/A"

# ============ COMPONENT BUILDERS ============
def render_process_tab():
    """Render the upload card for the Process tab"""
    return Div(
        Div(cls="card")(
            Div(cls="card-header")(
                H3("Upload QA Call Recording")
            ),
            Div(cls="card-body")(
                Form(
                    hx_post="/process_audio",
                    hx_target="#tab-content",
                    hx_swap="innerHTML",
                    hx_indicator="#loading-spinner",
                    enctype="multipart/form-data"
                )(
                    # Audio upload
                    Label("Audio File", style="font-weight: 500; display: block; margin-bottom: 4px;"),
                    Input(type="file", name="audio", accept="audio/*", required=True),

                    # Qualifiers section
                    Div(style="margin-top: 16px;")(
                        Div(style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;")(
                            Label("Qualifiers", style="font-weight: 500;"),
                            Label(style="font-size: 13px; color: var(--text-muted); cursor: pointer;")(
                                Input(type="checkbox", name="skip_qualifiers", id="skip-qual",
                                      style="margin-right: 6px;",
                                      onchange="document.getElementById('qualifiers-input').disabled = this.checked; document.getElementById('qualifiers-input').style.opacity = this.checked ? '0.5' : '1';"),
                                "Skip qualifiers"
                            )
                        ),
                        Textarea(name="qualifiers", id="qualifiers-input",
                                 placeholder="Paste qualifiers here:\n• KDMs (Key Decision Makers)\n• Timeline expectations\n• Disqualifiers\n• Company-specific criteria",
                                 style="min-height: 120px;")
                    ),

                    Button("Analyze Call", type="submit", style="margin-top: 12px;")
                )
            ),
            Div(cls="card-footer")(
                P("Supported formats: MP3, WAV, OGG, M4A", cls="info-text")
            )
        )
    )

def render_results_card(result_text, filename, timestamp, darts_score, show_saved_toast=False):
    """Render the results card after analysis"""
    # JavaScript for copy functionality
    copy_js = """
    var text = document.getElementById('result-text-content').innerText;
    navigator.clipboard.writeText(text).then(function() {
        var btn = document.getElementById('copy-btn');
        btn.innerText = '✓ Copied';
        btn.classList.add('copied');
        setTimeout(function() {
            btn.innerText = 'Copy';
            btn.classList.remove('copied');
        }, 2000);
    });
    """

    return Div(
        Div(cls="card")(
            Div(cls="card-header")(
                H3("Analysis Complete"),
                Div(
                    Button("Copy", id="copy-btn", cls="btn-copy", onclick=copy_js),
                    Span(f"{darts_score}/11", cls="darts-badge", style="margin-left: 8px;")
                )
            ),
            Div(cls="card-body scrollable")(
                Div(cls="metadata")(
                    P(Strong("File: "), filename),
                    P(Strong("Analyzed: "), timestamp)
                ),
                Div(result_text, cls="result-text", id="result-text-content")
            ),
            Div(cls="card-footer")(
                Button("Upload Another Call",
                       hx_get="/tab/process",
                       hx_target="#tab-content",
                       hx_swap="innerHTML",
                       onclick="document.getElementById('tab-process').classList.add('active');document.getElementById('tab-history').classList.remove('active')"),
                Button("Edit & Re-analyze",
                       hx_get="/edit_form",
                       hx_target="#tab-content",
                       hx_swap="innerHTML",
                       cls="btn-secondary")
            )
        ),
        # Toast notification
        Div("✓ Saved to history", id="save-toast", cls="toast show" if show_saved_toast else "toast"),
        # Auto-hide toast after 3 seconds
        Script("setTimeout(function(){ var t = document.getElementById('save-toast'); if(t) t.classList.remove('show'); }, 3000);") if show_saved_toast else None
    )

def render_history_card(record, idx):
    """Render a single history item card"""
    timestamp = record.get('Timestamp', 'Unknown')
    filename = record.get('Filename', 'Unknown')
    summary = record.get('Summary', '')[:150]
    full_result = record.get('Full Result', '')
    darts_score = extract_darts_score(full_result)

    return Div(cls="card history-item",
               hx_get=f"/result/{timestamp.replace(' ', '_').replace(':', '-')}",
               hx_target="#tab-content",
               hx_swap="innerHTML")(
        Div(cls="card-header")(
            Span(filename, cls="filename"),
            Span(f"{darts_score}/11", cls="darts-badge")
        ),
        Div(cls="card-body")(
            P(timestamp, cls="timestamp"),
            P(summary + "..." if summary else "No summary available", cls="summary")
        )
    )

# ============ HEALTH CHECK (for uptime monitoring) ============
@rt("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# ============ ROUTES ============

@rt("/login", methods=["GET", "POST"])
def login(req, sess, password: str = None):
    error_msg = None
    if req.method == "POST":
        if password == SESSION_PASSWORD:
            sess['auth'] = "authenticated"
            return RedirectResponse('/', status_code=303)
        error_msg = "Invalid password"

    return (
        Title("QA Tool - Login"),
        Div(cls="container", style="max-width: 400px; margin-top: 80px;")(
            Div(cls="card")(
                Div(cls="card-header")(
                    H3("QA Call Analyzer")
                ),
                Div(cls="card-body")(
                    P(error_msg, cls="error-text", style="margin-bottom: 12px;") if error_msg else None,
                    Form(method="post", action="/login")(
                        Input(name="password", type="password", placeholder="Enter password", required=True),
                        Button("Login", style="width: 100%;")
                    )
                )
            )
        )
    )

@rt("/logout")
def logout(sess):
    sess['auth'] = None
    return RedirectResponse('/login', status_code=303)

@rt("/")
def home(auth):
    return (
        Title("QA Call Analyzer"),
        Div(cls="container")(
            H1("QA Call Analyzer"),
            # Loading spinner overlay with processing text
            Div(id="loading-spinner", cls="spinner-overlay htmx-indicator")(
                Div(cls="processing-text")(
                    Div(cls="spinner"),
                    P("Processing with Gemini 2.0 Flash...")
                )
            ),
            # Tab navigation
            Div(cls="tabs")(
                Button("Process", cls="tab active", id="tab-process",
                       hx_get="/tab/process",
                       hx_target="#tab-content",
                       hx_swap="innerHTML",
                       onclick="document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));this.classList.add('active')"),
                Button("History", cls="tab", id="tab-history",
                       hx_get="/tab/history",
                       hx_target="#tab-content",
                       hx_swap="innerHTML",
                       onclick="document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));this.classList.add('active')")
            ),
            # Tab content container
            Div(id="tab-content")(
                render_process_tab()
            )
        )
    )

@rt("/tab/process")
def tab_process():
    """Return the Process tab content"""
    return render_process_tab()

@rt("/tab/history")
def tab_history():
    """Return the History tab content"""
    try:
        sheet = get_sheets_client()

        # Handle mock mode vs real sheets
        if sheet is None:
            records = mock_sheet_data
        else:
            records = sheet.get_all_records()

        if not records:
            return Div(cls="empty-state")(
                P("No call analyses yet."),
                P("Upload a call recording to get started!")
            )

        # Reverse to show newest first, limit to 50
        records_copy = list(records)
        records_copy.reverse()
        records_copy = records_copy[:50]

        return Div(cls="history-grid")(
            *[render_history_card(record, idx) for idx, record in enumerate(records_copy)]
        )

    except Exception as e:
        return Div(cls="card")(
            Div(cls="card-body")(
                P(f"Error loading history: {str(e)}", cls="error-text")
            )
        )

@rt("/result/{timestamp}")
def view_result(timestamp: str):
    """View a specific result from history"""
    try:
        # Convert timestamp back from URL format
        timestamp_clean = timestamp.replace('_', ' ').replace('-', ':')

        sheet = get_sheets_client()
        records = mock_sheet_data if sheet is None else sheet.get_all_records()

        # Find the record with matching timestamp
        record = None
        for r in records:
            if r.get('Timestamp', '') == timestamp_clean:
                record = r
                break

        if not record:
            return Div(cls="card")(
                Div(cls="card-body")(
                    P("Result not found", cls="error-text"),
                    Button("Back to History",
                           hx_get="/tab/history",
                           hx_target="#tab-content",
                           hx_swap="innerHTML",
                           onclick="document.getElementById('tab-history').classList.add('active');document.getElementById('tab-process').classList.remove('active')")
                )
            )

        filename = record.get('Filename', 'Unknown')
        result_text = record.get('Full Result', '')
        darts_score = extract_darts_score(result_text)

        return Div(
            Div(cls="card")(
                Div(cls="card-header")(
                    H3("Analysis Details"),
                    Span(f"{darts_score}/11", cls="darts-badge")
                ),
                Div(cls="card-body scrollable")(
                    Div(cls="metadata")(
                        P(Strong("File: "), filename),
                        P(Strong("Analyzed: "), timestamp_clean)
                    ),
                    Div(result_text, cls="result-text")
                ),
                Div(cls="card-footer")(
                    Button("Back to History",
                           hx_get="/tab/history",
                           hx_target="#tab-content",
                           hx_swap="innerHTML",
                           onclick="document.getElementById('tab-history').classList.add('active');document.getElementById('tab-process').classList.remove('active')")
                )
            )
        )

    except Exception as e:
        return Div(cls="card")(
            Div(cls="card-body")(
                P(f"Error loading result: {str(e)}", cls="error-text")
            )
        )

@rt("/process_audio", methods=["POST"])
async def process_audio(audio: UploadFile, sess, qualifiers: str = "", skip_qualifiers: str = None):
    try:
        # Read audio bytes
        audio_bytes = await audio.read()

        # Determine MIME type
        ext = audio.filename.lower().split('.')[-1]
        mime_map = {'mp3': 'audio/mp3', 'wav': 'audio/wav', 'ogg': 'audio/ogg', 'm4a': 'audio/mp4'}
        mime_type = mime_map.get(ext, 'audio/mpeg')

        # Build qualifiers context for Gemini
        qualifiers_context = ""
        if skip_qualifiers != "on" and qualifiers.strip():
            qualifiers_context = f"""

## QUALIFIERS TO CHECK AGAINST:
{qualifiers.strip()}

IMPORTANT: Use these qualifiers to verify appointment qualification in Section 7. Check if the prospect matches the qualifiers (KDMs, timeline, size thresholds) and note any disqualifiers mentioned.
"""

        # Call Gemini with QA prompt or use mock data
        if gemini_client is None:
            # Mock mode - return sample QA analysis
            result_text = f"""MOCK ANALYSIS FOR: {audio.filename}

## 1. INTRODUCTION
### A. NON-FOLLOW UP CALL
- RLM Stated: Done ✓
- Value Differentiator: Done ✓
- Objection Takeaway: Not Done ✗
- 1st Open-Ended Question: Done ✓

## 2. RELEVANT TOPICS
- Asked about services/capabilities: Done ✓
- Asked about most consistent issue: Done ✓

## 3. CLOSE
- Assumed close with 2 suggested dates/times: Done ✓
- Attempted to schedule within 5 business days: Done ✓
- Meeting Date & Time Confirmed: Done ✓
- Meeting Type (In-Person / Virtual / Phone): Virtual

## 4. OBJECTION HANDLING
- Used "Feel, Felt, Found": Not Done ✗
- Used "Worst Case Scenario": Not Done ✗
- Count number of objections: 2 objections

## 10. DARTS SCORE

**D = Desire to Meet:** 1 – Reason: Two objections raised
**A = Authority:** 2 – Reason: Final KDM confirmed
**R = Revenue Opportunity:** 2 – Reason: Strong interest shown
**T = Timeliness:** 2 – Reason: 0-6 months timeline
**S = Size:** 1 – Reason: Qualified opportunity

**TOTAL DARTS SCORE: [8/11]**

---

## 11. FEEDBACK

**Intro:** Good RLM and value introduction. Could strengthen objection handling.

**Relevant Topics:** Excellent open-ended questions about services and pain points.

**Close:** Strong assumptive close with clear dates. Meeting confirmed for next week.

**Objection Handling:** Limited objection techniques used. Consider Feel/Felt/Found framework.

**Documentation:** All contact info verified and confirmed. Ready for follow-up.

---

*This is MOCK data for UI testing (no API key)*"""
        else:
            # Combine QA prompt with qualifiers context
            full_prompt = QA_PROMPT + qualifiers_context
            response = gemini_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[
                    full_prompt,
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
                ]
            )
            result_text = response.text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to Google Sheets or mock storage
        try:
            sheet = get_sheets_client()
            if sheet is not None:
                sheet.append_row([
                    timestamp,
                    audio.filename,
                    result_text[:500],  # Summary (first 500 chars)
                    result_text         # Full response
                ])
            else:
                # Mock mode - store in memory
                global mock_sheet_data
                mock_sheet_data.append({
                    'Timestamp': timestamp,
                    'Filename': audio.filename,
                    'Summary': result_text[:500],
                    'Full Result': result_text
                })
        except Exception as e:
            result_text += f"\n\n⚠️ Failed to save: {e}"

        # Store result in session for edit/reanalyze
        sess['last_result'] = result_text
        sess['last_filename'] = audio.filename

        # Extract DARTS score and return results card with toast
        darts_score = extract_darts_score(result_text)
        return render_results_card(result_text, audio.filename, timestamp, darts_score, show_saved_toast=True)

    except Exception as e:
        return Div(cls="card")(
            Div(cls="card-body")(
                P(f"Error: {str(e)}", cls="error-text"),
                Button("Try Again",
                       hx_get="/tab/process",
                       hx_target="#tab-content",
                       hx_swap="innerHTML")
            )
        )

@rt("/edit_form")
def edit_form(sess):
    """Show edit form with last result text from session"""
    result_text = sess.get('last_result', '')
    filename = sess.get('last_filename', 'Unknown')

    if not result_text:
        return Div(cls="card")(
            Div(cls="card-body")(
                P("No recent result to edit.", cls="error-text"),
                Button("Back to Upload",
                       hx_get="/tab/process",
                       hx_target="#tab-content",
                       hx_swap="innerHTML")
            )
        )

    return Div(
        Div(cls="card")(
            Div(cls="card-header")(
                H3("Edit & Re-analyze")
            ),
            Div(cls="card-body")(
                P(f"Editing result for: {filename}", cls="info-text", style="margin-bottom: 12px;"),
                Form(
                    hx_post="/reanalyze",
                    hx_target="#tab-content",
                    hx_swap="innerHTML",
                    hx_indicator="#loading-spinner"
                )(
                    Textarea(name="edited_text", placeholder="Edit the analysis text...")(result_text),
                    Button("Re-analyze", type="submit")
                )
            ),
            Div(cls="card-footer")(
                Button("Cancel",
                       hx_get="/tab/process",
                       hx_target="#tab-content",
                       hx_swap="innerHTML",
                       cls="btn-secondary",
                       onclick="document.getElementById('tab-process').classList.add('active');document.getElementById('tab-history').classList.remove('active')")
            )
        )
    )

@rt("/reanalyze", methods=["POST"])
async def reanalyze(edited_text: str, sess):
    """Re-analyze edited text using Gemini"""
    try:
        # Send edited text to Gemini for re-analysis or use mock
        if gemini_client is None:
            # Mock mode - just return the edited text with a note
            result_text = edited_text + "\n\n---\n*Re-analyzed (MOCK MODE - no API key)*"
        else:
            response = gemini_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[
                    "Re-analyze and correct this QA call analysis based on any edits made. Maintain the same structured format:\n\n",
                    edited_text
                ]
            )
            result_text = response.text

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = "Re-analyzed"

        # Save to Google Sheets or mock storage
        try:
            sheet = get_sheets_client()
            if sheet is not None:
                sheet.append_row([
                    timestamp,
                    filename,
                    result_text[:500],
                    result_text
                ])
            else:
                # Mock mode - store in memory
                global mock_sheet_data
                mock_sheet_data.append({
                    'Timestamp': timestamp,
                    'Filename': filename,
                    'Summary': result_text[:500],
                    'Full Result': result_text
                })
        except Exception as e:
            result_text += f"\n\n⚠️ Failed to save: {e}"

        # Update session
        sess['last_result'] = result_text
        sess['last_filename'] = filename

        darts_score = extract_darts_score(result_text)
        return render_results_card(result_text, filename, timestamp, darts_score, show_saved_toast=True)

    except Exception as e:
        return Div(cls="card")(
            Div(cls="card-body")(
                P(f"Error: {str(e)}", cls="error-text"),
                Button("Try Again",
                       hx_get="/edit_form",
                       hx_target="#tab-content",
                       hx_swap="innerHTML")
            )
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
