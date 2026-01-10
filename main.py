from fasthtml.common import *
from datetime import datetime
import pytz
import os

from config import SESSION_SECRET, CSS
from handlers import (
    analyze_audio, analyze_transcript, reanalyze_text, extract_darts_score,
    save_result, get_history, find_record_by_timestamp
)
from components import (
    render_process_tab, render_results_card, render_history_card,
    render_edit_form, render_result_detail
)

app, rt = fast_app(
    secret_key=SESSION_SECRET,
    hdrs=(
        Script(src="https://unpkg.com/htmx.org@1.9.10"),
        Style(CSS),
    )
)


# ============ HEALTH CHECK ============
@rt("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# ============ MAIN ROUTES ============
@rt("/")
def home():
    return (
        Title("QA Call Analyzer"),
        Div(cls="container")(
            H1("QA Call Analyzer"),
            Div(id="loading-spinner", cls="spinner-overlay htmx-indicator")(
                Div(cls="processing-text")(
                    Div(cls="spinner"),
                    P("Processing with Gemini 2.0 Flash...")
                )
            ),
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
                       hx_indicator="#history-loading",
                       onclick="document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));this.classList.add('active');document.getElementById('tab-content').innerHTML='<div class=\"history-loading\"><div class=\"spinner\"></div><p>Loading history...</p></div>'")
            ),
            Div(id="tab-content")(
                render_process_tab()
            )
        )
    )


@rt("/tab/process")
def tab_process():
    return render_process_tab()


@rt("/tab/history")
def tab_history():
    try:
        records = get_history()

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
    try:
        timestamp_clean = timestamp.replace('_', ' ').replace('-', ':')
        record = find_record_by_timestamp(timestamp_clean)

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

        return render_result_detail(record, timestamp_clean)

    except Exception as e:
        return Div(cls="card")(
            Div(cls="card-body")(
                P(f"Error loading result: {str(e)}", cls="error-text")
            )
        )


# ============ PROCESSING ROUTES ============
@rt("/process_call", methods=["POST"])
async def process_call(sess, input_mode: str = "audio", audio: UploadFile = None, transcript: str = "", qualifiers: str = "", skip_qualifiers: str = None):
    try:
        is_transcript_mode = input_mode == "transcript"
        source_name = "Transcript" if is_transcript_mode else (audio.filename if audio else "Unknown")

        # Build qualifiers context
        qualifiers_context = ""
        if skip_qualifiers != "on" and qualifiers.strip():
            qualifiers_context = f"""

## QUALIFIERS TO CHECK AGAINST:
{qualifiers.strip()}

IMPORTANT: Use these qualifiers to verify appointment qualification in Section 7. Check if the prospect matches the qualifiers (KDMs, timeline, size thresholds) and note any disqualifiers mentioned.
"""

        # Analyze with Gemini
        if is_transcript_mode:
            result_text = analyze_transcript(transcript, qualifiers_context)
        else:
            audio_bytes = await audio.read()
            ext = audio.filename.lower().split('.')[-1]
            mime_map = {'mp3': 'audio/mp3', 'wav': 'audio/wav', 'ogg': 'audio/ogg', 'm4a': 'audio/mp4'}
            mime_type = mime_map.get(ext, 'audio/mpeg')
            result_text = analyze_audio(audio_bytes, mime_type, qualifiers_context)

        # Generate timestamp
        manila = pytz.timezone('Asia/Manila')
        timestamp = datetime.now(manila).strftime("%Y-%m-%d %I:%M:%S %p PHT")
        darts_score = extract_darts_score(result_text)

        # Save to storage
        if not save_result(timestamp, source_name, result_text):
            result_text += "\n\n⚠️ Failed to save to history"

        # Store in session for edit/reanalyze
        sess['last_result'] = result_text
        sess['last_filename'] = source_name

        return render_results_card(result_text, source_name, timestamp, darts_score, show_saved_toast=True)

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

    return render_edit_form(result_text, filename)


@rt("/reanalyze", methods=["POST"])
async def reanalyze(edited_text: str, sess):
    try:
        result_text = reanalyze_text(edited_text)

        manila = pytz.timezone('Asia/Manila')
        timestamp = datetime.now(manila).strftime("%Y-%m-%d %I:%M:%S %p PHT")
        filename = "Re-analyzed"
        darts_score = extract_darts_score(result_text)

        if not save_result(timestamp, filename, result_text):
            result_text += "\n\n⚠️ Failed to save to history"

        sess['last_result'] = result_text
        sess['last_filename'] = filename

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


# ============ START SERVER ============
if __name__ == '__main__':
    serve(port=int(os.getenv("PORT", 5001)))
