import re
from google import genai
from google.genai import types
from config import QA_PROMPT

# ============ GEMINI CLIENT ============
try:
    gemini_client = genai.Client()  # Uses GOOGLE_API_KEY env var
except ValueError:
    gemini_client = None  # Mock mode for local testing


def extract_darts_score(text: str) -> str:
    """Extract DARTS score from result text"""
    match = re.search(r'TOTAL DARTS SCORE:\s*\[?(\d+)/11\]?', text)
    return match.group(1) if match else "N/A"


def analyze_audio(audio_bytes: bytes, mime_type: str, qualifiers_context: str = "") -> str:
    """Send audio to Gemini for transcription and analysis"""
    if gemini_client is None:
        return _mock_analysis("Audio file")

    full_prompt = QA_PROMPT + qualifiers_context
    response = gemini_client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[
            full_prompt,
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        ]
    )
    return response.text


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
