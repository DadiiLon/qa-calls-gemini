import os
import json
import gspread

# In-memory storage for mock mode
mock_sheet_data = []

# Check if we have credentials for real mode
_has_credentials = "GOOGLE_SERVICE_ACCOUNT_JSON" in os.environ and "GOOGLE_API_KEY" in os.environ


def get_sheets_client():
    """Get Google Sheets client, or None for mock mode"""
    if not _has_credentials:
        return None
    creds = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    gc = gspread.service_account_from_dict(creds)
    return gc.open("QA Results").sheet1


def save_result(timestamp: str, filename: str, result_text: str) -> bool:
    """Save result to Google Sheets or mock storage. Returns True on success."""
    global mock_sheet_data

    try:
        sheet = get_sheets_client()
        if sheet is not None:
            sheet.append_row([
                timestamp,
                filename,
                result_text
            ])
        else:
            mock_sheet_data.append({
                'Timestamp': timestamp,
                'Filename': filename,
                'Full Result': result_text
            })
        return True
    except Exception:
        return False


def get_history() -> list:
    """Get all records from Sheets or mock storage"""
    sheet = get_sheets_client()
    if sheet is None:
        return mock_sheet_data
    return sheet.get_all_records()


def find_record_by_timestamp(timestamp: str) -> dict | None:
    """Find a specific record by timestamp"""
    records = get_history()
    for r in records:
        if r.get('Timestamp', '') == timestamp:
            return r
    return None
