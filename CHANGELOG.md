# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2026-01-11

### Fixed
- Timestamp URL encoding breaking history item clicks (colons now encoded as `~`)
- History tab stuck on loading when Sheets credentials invalid

### Changed
- Timezone from US/Eastern to Asia/Manila (PHT)
- README made beginner-friendly with detailed explanations
- Links in README now open in new tabs
- Cron expression section with visual breakdown and examples

### Removed
- Password protection / login page (app now directly accessible)

## [1.1.0] - 2026-01-11

### Added
- `.env.example` template file
- This changelog

### Changed
- Refactored codebase into modular structure (config, handlers, components)
- Simplified Google Sheets output to 3 columns (Timestamp, Filename, Full Result)
- README restructured: Render hosting first, local development second
- Added cold start info and cron-job.org keep-alive instructions

### Removed
- DARTS score column from Sheets output
- Summary column from Sheets output
- `FEEDBACK.md` and `qa_calls_with_gemini.md` spec files

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
- Card-based UI with Process/History tabs
- Password-protected sessions
- Health endpoint for uptime monitoring
- Loading states and toast notifications

### Changed
- Upgraded from Gemini 1.5 to 2.0 Flash
- Moved QA prompt to environment variable for security
