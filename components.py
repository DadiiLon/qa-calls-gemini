from fasthtml.common import *
import markdown
import re
from handlers import extract_darts_score


def render_process_tab():
    """Render the upload card for the Process tab"""
    validation_js = """
    function validateForm() {
        var skipChecked = document.getElementById('skip-qual').checked;
        var qualifiersText = document.getElementById('qualifiers-input').value.trim();
        var analyzeBtn = document.getElementById('analyze-btn');
        var inputMode = document.querySelector('input[name="input_mode"]:checked').value;

        var qualifiersOk = skipChecked || qualifiersText.length > 0;

        var inputOk = false;
        if (inputMode === 'audio') {
            var audioInput = document.getElementById('audio-input');
            inputOk = audioInput && audioInput.files && audioInput.files.length > 0;
        } else {
            var transcriptInput = document.getElementById('transcript-input');
            inputOk = transcriptInput && transcriptInput.value.trim().length > 0;
        }

        analyzeBtn.disabled = !(qualifiersOk && inputOk);
    }

    function handleSkipChange() {
        var skipChecked = document.getElementById('skip-qual').checked;
        var qualInput = document.getElementById('qualifiers-input');
        qualInput.disabled = skipChecked;
        qualInput.style.opacity = skipChecked ? '0.5' : '1';
        validateForm();
    }

    function switchInputMode(mode) {
        var audioSection = document.getElementById('audio-section');
        var transcriptSection = document.getElementById('transcript-section');

        if (mode === 'audio') {
            audioSection.style.display = 'block';
            transcriptSection.style.display = 'none';
        } else {
            audioSection.style.display = 'none';
            transcriptSection.style.display = 'block';
        }
        validateForm();
    }

    document.addEventListener('DOMContentLoaded', validateForm);

    function triggerFileInput() {
        document.getElementById('audio-input').click();
    }

    function updateFileButton() {
        var input = document.getElementById('audio-input');
        var btn = document.getElementById('upload-btn');
        if (input.files && input.files.length > 0) {
            btn.textContent = input.files[0].name;
            btn.classList.add('file-selected');
        } else {
            btn.textContent = 'Upload Audio';
            btn.classList.remove('file-selected');
        }
        validateForm();
    }
    """

    return Div(
        Script(validation_js),
        Div(cls="card")(
            Div(cls="card-header")(
                H3("Analyze QA Call")
            ),
            Div(cls="card-body")(
                Form(
                    hx_post="/process_call",
                    hx_target="#tab-content",
                    hx_swap="innerHTML",
                    enctype="multipart/form-data",
                    **{"hx-on::before-request": "document.getElementById('tab-content').innerHTML='<div class=\"card\"><div class=\"card-body\"><div class=\"processing-text\"><div class=\"spinner\"></div><p>Processing with Gemini 2.0 Flash...</p></div></div></div>'"}
                )(
                    # Input mode selector
                    Div(style="margin-bottom: 16px;")(
                        Label("Input Type", style="font-weight: 500; display: block; margin-bottom: 8px;"),
                        Div(style="display: flex; gap: 24px;")(
                            Label(style="display: flex; align-items: center; cursor: pointer;")(
                                Input(type="radio", name="input_mode", value="audio", checked=True,
                                      style="margin-right: 8px;",
                                      onchange="switchInputMode('audio')"),
                                "Upload Audio"
                            ),
                            Label(style="display: flex; align-items: center; cursor: pointer;")(
                                Input(type="radio", name="input_mode", value="transcript",
                                      style="margin-right: 8px;",
                                      onchange="switchInputMode('transcript')"),
                                "Paste Transcript"
                            )
                        )
                    ),

                    # Audio upload section
                    Div(id="audio-section")(
                        Input(type="file", name="audio", id="audio-input", accept="audio/*",
                              onchange="updateFileButton()", style="display: none;"),
                        Button("Upload Audio", type="button", id="upload-btn", cls="upload-btn",
                               onclick="triggerFileInput()")
                    ),

                    # Transcript paste section (hidden by default)
                    Div(id="transcript-section", style="display: none;")(
                        Label("Call Transcript", style="font-weight: 500; display: block; margin-bottom: 4px;"),
                        Textarea(name="transcript", id="transcript-input",
                                 placeholder="Paste the full call transcript here...",
                                 style="min-height: 200px;",
                                 oninput="validateForm()")
                    ),

                    # Qualifiers section
                    Div(style="margin-top: 16px;")(
                        Div(style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;")(
                            Label("Qualifiers", style="font-weight: 500;"),
                            Label(style="font-size: 13px; color: var(--text-muted); cursor: pointer;")(
                                Input(type="checkbox", name="skip_qualifiers", id="skip-qual",
                                      style="margin-right: 6px;",
                                      onchange="handleSkipChange()"),
                                "Skip qualifiers"
                            )
                        ),
                        Textarea(name="qualifiers", id="qualifiers-input",
                                 style="min-height: 120px;",
                                 oninput="validateForm()")
                    ),

                    Button("Analyze Call", type="submit", id="analyze-btn", disabled=True, style="margin-top: 12px;")
                )
            )
        )
    )


def render_results_card(result_text: str, filename: str, timestamp: str, darts_score: str, show_saved_toast: bool = False):
    """Render the results card after analysis"""
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
                Button("Copy", id="copy-btn", cls="btn-copy", onclick=copy_js)
            ),
            Div(cls="card-body scrollable")(
                Div(cls="metadata")(
                    P(Strong("File: "), filename),
                    P(Strong("Analyzed: "), timestamp)
                ),
                Div(NotStr(markdown.markdown(result_text.replace('\\"', '"'))), cls="result-text", id="result-text-content")
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
        Div("✓ Saved to history", id="save-toast", cls="toast show" if show_saved_toast else "toast"),
        Script("setTimeout(function(){ var t = document.getElementById('save-toast'); if(t) t.classList.remove('show'); }, 3000);") if show_saved_toast else None
    )


def render_history_card(record: dict, idx: int):
    """Render a single history item card"""
    timestamp = record.get('Timestamp', 'Unknown')
    filename = record.get('Filename', 'Unknown')
    summary = record.get('Summary', '')[:150]
    full_result = record.get('Full Result', '')
    darts_score = extract_darts_score(full_result)

    return Div(cls="card history-item",
               hx_get=f"/result/{timestamp.replace(' ', '_').replace(':', '~')}",
               hx_target="#tab-content",
               hx_swap="innerHTML")(
        Div(cls="card-header")(
            Span(filename, cls="filename")
        ),
        Div(cls="card-body")(
            P(timestamp, cls="timestamp"),
            P(summary + "..." if summary else "No summary available", cls="summary")
        )
    )


def render_edit_form(result_text: str, filename: str):
    """Render the edit form for re-analysis"""
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


def render_result_detail(record: dict, timestamp_clean: str, timestamp_encoded: str):
    """Render full result detail view from history with sub-tabs"""
    filename = record.get('Filename', 'Unknown')
    result_text = record.get('Full Result', '')
    transcript = record.get('Transcript', '')
    audio_url = record.get('Audio_URL', '')
    darts_score = extract_darts_score(result_text)

    # Check if transcript is available
    has_transcript = bool(transcript and transcript.strip())

    # Sub-tab switching JavaScript
    subtab_js = """
    function switchDetailTab(tab) {
        document.querySelectorAll('.sub-tab').forEach(function(t) {
            t.classList.remove('active');
        });
        event.target.classList.add('active');
    }
    """

    return Div(
        Script(subtab_js),
        Div(cls="card")(
            Div(cls="card-header")(
                H3("Analysis Details")
            ),
            # Sub-tabs
            Div(cls="sub-tabs")(
                Button("Analysis", cls="sub-tab active",
                       hx_get=f"/result/{timestamp_encoded}/analysis",
                       hx_target="#detail-content",
                       hx_swap="innerHTML",
                       onclick="switchDetailTab('analysis')"),
                Button("Transcript", cls="sub-tab" + (" disabled" if not has_transcript else ""),
                       hx_get=f"/result/{timestamp_encoded}/transcript",
                       hx_target="#detail-content",
                       hx_swap="innerHTML",
                       onclick="switchDetailTab('transcript')",
                       disabled=not has_transcript,
                       title="" if has_transcript else "No transcript available for this record")
            ),
            # Content area (default to analysis view)
            Div(id="detail-content")(
                render_analysis_content(result_text, filename, timestamp_clean)
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


def render_analysis_content(result_text: str, filename: str, timestamp_clean: str):
    """Render the analysis tab content"""
    return Div(cls="card-body scrollable")(
        Div(cls="metadata")(
            P(Strong("File: "), filename),
            P(Strong("Analyzed: "), timestamp_clean)
        ),
        Div(NotStr(markdown.markdown(result_text.replace('\\"', '"'))), cls="result-text")
    )


def parse_transcript_lines(transcript: str) -> list:
    """Parse transcript and merge consecutive same-speaker lines"""
    lines = transcript.split('\n')
    merged = []
    current_speaker = None
    current_texts = []

    for line in lines:
        # Parse line format: [MM:SS] Speaker: Text
        match = re.match(r'\[(\d+:\d+)\]\s*(\w+):\s*(.*)', line.strip())
        if not match:
            continue

        speaker = match.group(2)
        text = match.group(3).strip()

        if not text:
            continue

        # Normalize speaker name
        speaker_lower = speaker.lower()
        if speaker_lower == current_speaker:
            # Same speaker, append text
            current_texts.append(text)
        else:
            # Different speaker, save previous and start new
            if current_speaker and current_texts:
                merged.append({
                    'speaker': current_speaker,
                    'text': ' '.join(current_texts)
                })
            current_speaker = speaker_lower
            current_texts = [text]

    # Don't forget the last speaker
    if current_speaker and current_texts:
        merged.append({
            'speaker': current_speaker,
            'text': ' '.join(current_texts)
        })

    return merged


def render_transcript_line_simple(entry: dict):
    """Render a merged transcript line without timestamps"""
    speaker = entry['speaker']
    text = entry['text']

    # Determine speaker class and display name
    if speaker == "agent":
        speaker_class = "speaker-agent"
        display_name = "Agent"
    else:
        speaker_class = "speaker-client"
        display_name = "Client"

    return Div(cls="transcript-line")(
        Span(f"{display_name}: ", cls=f"speaker-label {speaker_class}"),
        Span(text, cls="transcript-text")
    )


def render_transcript_content(transcript: str, audio_url: str | None, filename: str, timestamp_clean: str):
    """Render the transcript tab content with audio player (no timestamp sync)"""
    # Parse and merge consecutive same-speaker lines
    merged_lines = parse_transcript_lines(transcript)
    transcript_elements = [render_transcript_line_simple(entry) for entry in merged_lines]

    return Div(
        Div(cls="card-body scrollable")(
            Div(cls="metadata")(
                P(Strong("File: "), filename),
                P(Strong("Analyzed: "), timestamp_clean)
            ),
            # Audio player (only if audio_url is available)
            Div(cls="audio-player-container")(
                Audio(id="audio-player", controls=True, cls="audio-player", src=audio_url) if audio_url else None,
                P("Audio not available for this recording", cls="info-text") if not audio_url else None
            ) if audio_url else None,
            # Transcript content
            Div(cls="transcript-container")(
                *transcript_elements if transcript_elements else [P("Transcript is empty", cls="info-text")]
            )
        )
    )
