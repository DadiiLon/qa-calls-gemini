# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-01-11

### Changed
- Refactored codebase into modular structure (config, handlers, components)
- Simplified Google Sheets output to 3 columns (Timestamp, Filename, Full Result)
- Updated README with complete setup guide

### Removed
- DARTS score column from Sheets output
- Summary column from Sheets output

## [1.0.0] - 2026-01-10

### Added
- Audio upload support (.mp3, .wav, .m4a, .ogg)
- Transcript paste input option
- Qualifiers input with skip toggle
- Gemini 2.0 Flash integration for analysis
- Google Sheets storage for results
- History view (last 50 analyses)
- Edit & re-analyze functionality
- Copy to clipboard button
- Dark theme UI
- Password-protected sessions
- Health endpoint for uptime monitoring
- Loading states and toast notifications

### Changed
- Upgraded from Gemini 1.5 to 2.0 Flash
- Moved QA prompt to environment variable for security
