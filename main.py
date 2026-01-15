from fasthtml.common import *
from datetime import datetime
import pytz
import os

from config import SESSION_SECRET, CSS
from handlers import (
    analyze_audio, analyze_transcript, reanalyze_text, extract_darts_score,
    save_result, get_history, find_record_by_timestamp,
    upload_audio, get_audio_url, get_mock_audio
)
from components import (
    render_process_tab, render_results_card, render_history_card,
    render_edit_form, render_result_detail, render_analysis_content,
    render_transcript_content
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
        timestamp_clean = timestamp.replace('_', ' ').replace('~', ':')
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

        # Get signed URL for audio if available
        audio_blob = record.get('Audio_URL', '')
        if audio_blob:
            record['Audio_URL'] = get_audio_url(audio_blob) or ''

        return render_result_detail(record, timestamp_clean, timestamp)

    except Exception as e:
        return Div(cls="card")(
            Div(cls="card-body")(
                P(f"Error loading result: {str(e)}", cls="error-text")
            )
        )


@rt("/result/{timestamp}/analysis")
def view_result_analysis(timestamp: str):
    """Return just the analysis content for HTMX swap"""
    try:
        timestamp_clean = timestamp.replace('_', ' ').replace('~', ':')
        record = find_record_by_timestamp(timestamp_clean)

        if not record:
            return P("Result not found", cls="error-text")

        filename = record.get('Filename', 'Unknown')
        result_text = record.get('Full Result', '')

        return render_analysis_content(result_text, filename, timestamp_clean)

    except Exception as e:
        return P(f"Error: {str(e)}", cls="error-text")


@rt("/result/{timestamp}/transcript")
def view_result_transcript(timestamp: str):
    """Return just the transcript content for HTMX swap"""
    try:
        timestamp_clean = timestamp.replace('_', ' ').replace('~', ':')
        record = find_record_by_timestamp(timestamp_clean)

        if not record:
            return P("Result not found", cls="error-text")

        filename = record.get('Filename', 'Unknown')
        transcript = record.get('Transcript', '')
        audio_blob = record.get('Audio_URL', '')

        # Get signed URL for audio if available
        audio_url = None
        if audio_blob:
            audio_url = get_audio_url(audio_blob)

        if not transcript:
            return Div(cls="card-body")(
                P("No transcript available for this record.", cls="info-text"),
                P("Transcripts are only available for new audio uploads.", cls="info-text")
            )

        return render_transcript_content(transcript, audio_url, filename, timestamp_clean)

    except Exception as e:
        return P(f"Error: {str(e)}", cls="error-text")


@rt("/api/audio")
def serve_audio(request, file: str = ""):
    """Serve audio file (for mock mode) or redirect to signed URL with range request support"""
    blob_name = file
    if not blob_name:
        return Response(content="No file specified", status_code=400)

    # Check if this is mock audio
    mock_bytes = get_mock_audio(blob_name)
    if mock_bytes:
        # Determine content type
        content_type = "audio/mpeg"
        if blob_name.lower().endswith(".wav"):
            content_type = "audio/wav"
        elif blob_name.lower().endswith(".m4a"):
            content_type = "audio/mp4"
        elif blob_name.lower().endswith(".ogg"):
            content_type = "audio/ogg"

        file_size = len(mock_bytes)
        range_header = request.headers.get("range")

        if range_header:
            # Parse range header (e.g., "bytes=0-1000")
            try:
                range_spec = range_header.replace("bytes=", "")
                start_str, end_str = range_spec.split("-")
                start = int(start_str) if start_str else 0
                end = int(end_str) if end_str else file_size - 1
                end = min(end, file_size - 1)

                content_length = end - start + 1
                return Response(
                    content=mock_bytes[start:end + 1],
                    status_code=206,
                    media_type=content_type,
                    headers={
                        "Content-Range": f"bytes {start}-{end}/{file_size}",
                        "Accept-Ranges": "bytes",
                        "Content-Length": str(content_length),
                        "Content-Disposition": f"inline; filename={blob_name}"
                    }
                )
            except (ValueError, IndexError):
                pass  # Fall through to return full file

        # No range request - return full file
        return Response(
            content=mock_bytes,
            media_type=content_type,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
                "Content-Disposition": f"inline; filename={blob_name}"
            }
        )

    # For real mode, redirect to signed URL
    signed_url = get_audio_url(blob_name)
    if signed_url:
        return RedirectResponse(url=signed_url)

    return Response(content="Audio not found", status_code=404)


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

        # Generate timestamp early (needed for audio upload)
        manila = pytz.timezone('Asia/Manila')
        timestamp = datetime.now(manila).strftime("%Y-%m-%d %I:%M:%S %p PHT")

        # Initialize transcript and audio URL
        transcript_text = ""
        audio_blob_name = ""

        # Analyze with Gemini
        if is_transcript_mode:
            result_text = analyze_transcript(transcript, qualifiers_context)
            # No transcript extraction for pasted transcripts (already have it)
        else:
            # Validate audio file
            if not audio or not audio.filename:
                raise ValueError("No audio file provided")

            # Check content type from upload
            content_type = getattr(audio, 'content_type', '') or ''
            if not content_type.startswith('audio/'):
                raise ValueError("Only audio files are allowed")

            audio_bytes = await audio.read()

            # Validate file size (max 25MB for Gemini)
            if len(audio_bytes) > 25_000_000:
                raise ValueError("Audio file too large (max 25MB)")

            ext = audio.filename.lower().split('.')[-1]
            mime_map = {'mp3': 'audio/mp3', 'wav': 'audio/wav', 'ogg': 'audio/ogg', 'm4a': 'audio/mp4'}
            mime_type = mime_map.get(ext, content_type or 'audio/mpeg')

            # Upload audio to storage first
            audio_blob_name = upload_audio(audio_bytes, audio.filename, timestamp) or ""

            # Analyze audio (now returns dict with analysis and transcript)
            result = analyze_audio(audio_bytes, mime_type, qualifiers_context)
            result_text = result['analysis']
            transcript_text = result['transcript']

        darts_score = extract_darts_score(result_text)

        # Save to storage with transcript and audio URL
        if not save_result(timestamp, source_name, result_text, transcript_text, audio_blob_name):
            result_text += "\n\n⚠️ Failed to save to history"

        # Store in session for edit/reanalyze
        sess['last_result'] = result_text
        sess['last_filename'] = source_name

        # Get signed URL for audio playback
        audio_signed_url = get_audio_url(audio_blob_name) if audio_blob_name else ""

        return render_results_card(result_text, source_name, timestamp, darts_score,
                                   transcript=transcript_text, audio_url=audio_signed_url,
                                   show_saved_toast=True)

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
