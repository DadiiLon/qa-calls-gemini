import re
from google import genai
from google.genai import types
from config import QA_PROMPT

# ============ GEMINI CLIENT ============
try:
    gemini_client = genai.Client()  # Uses GOOGLE_API_KEY env var
except ValueError:
    gemini_client = None  # Mock mode for local testing

# Prompt for transcript extraction with timestamps and speaker labels
TRANSCRIPT_PROMPT = """Transcribe this audio with timestamps and speaker labels.

Format each line exactly as:
[MM:SS] Speaker: Text

Rules:
- Use [MM:SS] format for timestamps (e.g., [0:15], [1:30], [10:45])
- Identify speakers as "Agent" (the sales representative) and "Client" (the prospect/customer)
- Include a new timestamp every 10-15 seconds or when the speaker changes
- Capture the full conversation verbatim

Example output:
[0:00] Agent: Hello, thank you for calling ABC Company. My name is John.
[0:05] Client: Hi John, I'm calling about your services.
[0:12] Agent: I'd be happy to help you with that. Can you tell me more about what you're looking for?
"""


def extract_darts_score(text: str) -> str:
    """Extract DARTS score from result text"""
    match = re.search(r'TOTAL DARTS SCORE:\s*\[?(\d+)/11\]?', text)
    return match.group(1) if match else "N/A"


def analyze_audio(audio_bytes: bytes, mime_type: str, qualifiers_context: str = "") -> dict:
    """
    Send audio to Gemini for transcription and analysis.
    Returns dict with 'analysis' and 'transcript' keys.
    """
    if gemini_client is None:
        return {
            'analysis': _mock_analysis("Audio file"),
            'transcript': _mock_transcript()
        }

    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)

    # Get transcript with timestamps and speaker labels
    transcript_response = gemini_client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[TRANSCRIPT_PROMPT, audio_part]
    )
    transcript = transcript_response.text

    # Get QA analysis
    full_prompt = QA_PROMPT + qualifiers_context
    analysis_response = gemini_client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[full_prompt, audio_part]
    )
    analysis = analysis_response.text

    return {
        'analysis': analysis,
        'transcript': transcript
    }


def analyze_transcript(transcript: str, qualifiers_context: str = "") -> str:
    """Send transcript text to Gemini for analysis"""
    if gemini_client is None:
        return _mock_analysis("Transcript")

    full_prompt = QA_PROMPT + qualifiers_context
    response = gemini_client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[full_prompt + "\n\n## CALL TRANSCRIPT:\n" + transcript]
    )
    return response.text


def reanalyze_text(edited_text: str) -> str:
    """Re-analyze edited text using Gemini"""
    if gemini_client is None:
        return edited_text + "\n\n---\n*Re-analyzed (MOCK MODE - no API key)*"

    response = gemini_client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[
            "Re-analyze and correct this QA call analysis based on any edits made. Maintain the same structured format:\n\n",
            edited_text
        ]
    )
    return response.text


def _mock_analysis(source_name: str) -> str:
    """Return mock QA analysis for testing without API key"""
    return f"""MOCK ANALYSIS FOR: {source_name}

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


def _mock_transcript() -> str:
    """Return mock transcript for testing without API key"""
    return """[0:00] Agent: Hello, thank you for calling ABC Company. My name is John, and I'm reaching out because we help businesses like yours streamline their operations.
[0:08] Client: Hi John, thanks for calling. What exactly do you do?
[0:12] Agent: Great question! We provide enterprise software solutions that help companies reduce their IT costs by up to 40%. I noticed your company has been growing rapidly.
[0:22] Client: Yes, we've had quite a bit of growth this past year. Our current systems are struggling to keep up.
[0:28] Agent: That's exactly why I'm calling. Many of our clients faced similar challenges before working with us. Can you tell me more about what issues you're experiencing?
[0:38] Client: Well, mainly data synchronization between departments. It takes forever and we lose productivity.
[0:45] Agent: I completely understand. We actually specialize in real-time data integration. Would you be open to a brief demo to see how we could help?
[0:55] Client: I might be interested, but I need to check with my IT director first.
[1:02] Agent: Of course, that makes sense. Is your IT director the final decision maker for these types of purchases?
[1:08] Client: Yes, she handles all our technology decisions.
[1:12] Agent: Perfect. What if we scheduled a call that includes her? That way she can ask technical questions directly.
[1:20] Client: That could work. Let me check her calendar.
[1:25] Agent: Great! How does next Tuesday at 2 PM or Wednesday at 10 AM work for you both?
[1:32] Client: Tuesday at 2 PM should work. Let me confirm and get back to you.
[1:38] Agent: Excellent! I'll send you a calendar invite right now. What's the best email to reach you and your IT director?

---

*This is MOCK transcript data for UI testing (no API key)*"""
