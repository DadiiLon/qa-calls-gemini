import os
from dotenv import load_dotenv

load_dotenv()

# ============ SESSION CONFIG ============
SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-secret-change-in-prod")

# ============ QA PROMPT ============
QA_PROMPT = os.environ.get("QA_PROMPT", "QA_PROMPT not configured in .env")

# ============ CSS STYLES ============
CSS = """
:root {
    --primary: #3b82f6;
    --primary-hover: #2563eb;
    --bg: #0f0f0f;
    --card-bg: #1a1a1a;
    --card-bg-alt: #141414;
    --border: #2a2a2a;
    --border-light: #333;
    --text: #e5e5e5;
    --text-muted: #888;
    --success: #22c55e;
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
    max-width: 1200px;
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
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
}

.tab {
    padding: 12px 24px;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
    cursor: pointer;
    font-size: 15px;
    font-weight: 500;
    color: var(--text-muted);
    transition: all 0.15s;
}

.tab:hover { color: var(--text); }
.tab.active {
    color: var(--primary);
    border-bottom-color: var(--primary);
}

/* Cards */
.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
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
    color: var(--text);
}

.card-body { padding: 20px; }
.card-body.scrollable {
    max-height: 500px;
    overflow-y: auto;
}

.card-footer {
    padding: 16px 20px;
    border-top: 1px solid var(--border);
    background: var(--card-bg-alt);
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    border-radius: 0 0 var(--radius) var(--radius);
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
    background: var(--card-bg-alt);
    color: var(--text);
}

input[type="file"]::file-selector-button {
    background: var(--border-light);
    color: var(--text);
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    margin-right: 12px;
}

input[type="file"]::file-selector-button:hover {
    background: #444;
}

input:focus, textarea:focus {
    outline: none;
    border-color: var(--primary);
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

button:disabled {
    background: var(--border-light);
    color: var(--text-muted);
    cursor: not-allowed;
}

.btn-secondary {
    background: var(--border-light);
}
.btn-secondary:hover { background: #444; }

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
.metadata p { margin: 4px 0; color: var(--text-muted); }
.metadata strong { color: var(--text); }

/* Result text - rendered markdown */
.result-text {
    font-size: 0.8rem;
    line-height: 1.6;
    background: var(--card-bg-alt);
    padding: 16px;
    border-radius: var(--radius);
    border: 1px solid var(--border);
    color: var(--text);
}
.result-text h2 {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--primary);
    margin: 20px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
}
.result-text h2:first-child { margin-top: 0; }
.result-text h3 {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text);
    margin: 12px 0 6px 0;
}
.result-text ul {
    margin: 6px 0;
    padding-left: 18px;
}
.result-text li {
    margin: 3px 0;
}
.result-text p {
    margin: 6px 0;
}
.result-text strong {
    color: var(--text);
}
.result-text hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 20px 0;
}

/* History grid */
.history-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
}

.history-item { cursor: pointer; transition: all 0.15s; }
.history-item:hover {
    border-color: var(--border-light);
    transform: translateY(-2px);
}

.history-item .filename {
    font-weight: 600;
    font-size: 14px;
    word-break: break-all;
    color: var(--text);
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
    display: none;
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

/* History loading */
.history-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
}
.history-loading .spinner {
    width: 40px;
    height: 40px;
}
.history-loading p {
    margin-top: 16px;
    color: var(--text-muted);
}

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
    background: var(--border-light);
    padding: 6px 12px;
    font-size: 13px;
}
.btn-copy:hover { background: #444; }
.btn-copy.copied {
    background: var(--success);
}

/* Upload button */
.upload-btn {
    width: 100%;
    padding: 14px 20px;
    background: #151515;
    border: 1px solid var(--border-light);
    border-radius: var(--radius);
    color: var(--text-muted);
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.upload-btn:hover {
    transform: translateY(-2px);
    border-color: var(--accent);
    box-shadow: 0 4px 12px rgba(215, 119, 87, 0.2);
}
.upload-btn.file-selected {
    background: rgba(34, 197, 94, 0.1);
    border-color: var(--success);
    color: var(--text-primary);
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
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
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

/* Login page */
.login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.login-card {
    width: 100%;
    max-width: 380px;
}

.login-card .card-header {
    text-align: center;
    padding: 32px 20px 24px;
    border-bottom: none;
}

.login-card .card-header h3 {
    font-size: 22px;
}

.login-card .card-body {
    padding: 0 24px 32px;
}

.login-subtitle {
    text-align: center;
    color: var(--text-muted);
    font-size: 14px;
    margin-top: 8px;
}

/* Checkbox & Radio styling */
input[type="checkbox"],
input[type="radio"] {
    width: 16px;
    height: 16px;
    accent-color: var(--primary);
    cursor: pointer;
}

/* Label styling */
label {
    color: var(--text);
}

/* Sub-tabs (smaller than main tabs) */
.sub-tabs {
    display: flex;
    gap: 4px;
    padding: 0 20px;
    border-bottom: 1px solid var(--border);
    background: var(--card-bg-alt);
}

.sub-tab {
    padding: 10px 20px;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-muted);
    transition: all 0.15s;
}

.sub-tab:hover:not(:disabled) { color: var(--text); }
.sub-tab.active {
    color: var(--primary);
    border-bottom-color: var(--primary);
}
.sub-tab:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

/* Audio player */
.audio-player-container {
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
}

.audio-player {
    width: 100%;
    height: 40px;
    border-radius: var(--radius);
}

/* Transcript styling */
.transcript-container {
    background: var(--card-bg-alt);
    padding: 16px;
    border-radius: var(--radius);
    border: 1px solid var(--border);
    max-height: 400px;
    overflow-y: auto;
}

.transcript-line {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    line-height: 1.6;
}

.transcript-line:last-child {
    border-bottom: none;
}

.speaker-label {
    font-weight: 600;
    font-size: 13px;
}

.speaker-agent {
    color: #3b82f6;
}

.speaker-client {
    color: #22c55e;
}

.transcript-text {
    color: var(--text);
    font-size: 14px;
}

/* Side-by-side results layout */
.results-wrapper {
    display: block;
}

.results-wrapper.has-transcript {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    align-items: stretch;
}

.results-main {
    min-width: 0;
    display: flex;
    flex-direction: column;
}

.results-main .card {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.results-main .card-body.scrollable {
    flex: 1;
    max-height: 500px;
}

.results-sidebar {
    min-width: 0;
    display: flex;
    flex-direction: column;
}

.results-sidebar .card {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.results-sidebar .card-body.scrollable {
    flex: 1;
    max-height: 500px;
}

.results-sidebar .transcript-container {
    max-height: none;
}

/* Mobile responsive */
@media (max-width: 900px) {
    .results-wrapper.has-transcript {
        grid-template-columns: 1fr;
    }
    .results-sidebar {
        order: 1;
    }
}

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
    .sub-tabs { padding: 0 16px; }
    .sub-tab { padding: 8px 14px; font-size: 13px; }
    .transcript-container { padding: 12px; }
    .transcript-line { padding: 6px 0; }
}
"""
