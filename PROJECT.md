# Master Project Plan: PulseGrid Emergency Web App

## Architecture
- **Frontend**: Vanilla HTML5, CSS3, ES6 JavaScript (`public/index.html`, `public/hospital.html`, `public/js/api.js`, `public/js/triage.js`, `public/css/custom.css`), Google Maps JS API / Leaflet / OSRM mapping.
- **Backend**: Flask 3.0 WSGI service (`app.py`, `database.py`, `triage_service.py`, `ttl_worker.py`), REST APIs with dual Supabase PostgreSQL DB / In-memory Mock fallback modes.
- **Background Worker**: `ttl_worker.py` daemon thread running automatic TTL hold expiration release every 10s.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Full-Screen Map & Unified Search UI | R1: 100% full-screen map canvas (`#map`), floating top navbar, slidable bottom drawer sheet matching native Google Maps UI (rounded top edges, drag handle, clean metrics), unified search bar (symptom + blood type parser regex + Hinglish/Benglish/English voice input), map route fitting and bounds auto-zoom. | None | DONE |
| 2 | M2: Real-Time Soft/Hard-Lock Bed Reservation Engine | R2: 15-minute soft lock reserving 1 bed (bed count 30->29, OTP generation), backend endpoints (`/api/holds/create`, `/api/holds/redeem`, `/api/holds/location_update`, `/api/holds/cancel`), live GPS tracking vector loop (moving toward = live dynamic ETA + hide timer; stationary = countdown; moving away 2-3x = wrong direction alert & auto-cancel), hard-lock OTP verification. | M1 | DONE |
| 3 | M3: Stabilized Routing, Polling & Post-Booking UX | R3: Fix ETA recalculation jitter (throttled OSRM fetches), eliminate background auto-scroll bug (`scrollIntoView` fix in `highlightCard`), remove all judge/demo buttons & hospital desk tabs, post-booking drawer UI transformation (single-tap Call Ambulance & Call Hospital quick-dial buttons). | M1, M2 | DONE |
| 4 | M4: E2E Integration, Test Suite Pass & Hardening | Final Milestone: Pass 100% of E2E test suite (Tiers 1-4, 37 passing pytest cases), white-box coverage hardening, and Forensic Audit verification across all milestones. | M1, M2, M3, E2E Track | DONE |

## Interface Contracts
### Frontend ↔ Backend REST API
- `POST /api/search` / `POST /api/triage`: Accepts query payload `{ text: string, lat?: float, lng?: float, is_voice?: boolean }`. Returns category, triage level, recommended hospitals, and blood match info.
- `POST /api/holds/create`: Accepts `{ hospital_id: string, user_id?: string, hold_type?: string }`. Returns `{ success: true, hold_id: string, otp_code: string, expires_at: string, bed_count: int }`.
- `POST /api/holds/redeem`: Accepts `{ hold_id: string, otp_code: string }`. Returns `{ success: true, status: "REDEEMED", bed_count: int }`.
- `POST /api/holds/location_update`: Accepts `{ hold_id: string, user_lat: float, user_lng: float, heading?: float, speed?: float }`. Returns `{ status: "ACTIVE"|"CANCELLED", movement_direction: "TOWARD"|"STATIONARY"|"AWAY", current_eta_minutes: float, wrong_direction_count: int }`.
- `POST /api/holds/cancel`: Accepts `{ hold_id: string }`. Returns `{ success: true, status: "CANCELLED" }`.

## Code Layout
- Frontend: `public/index.html`, `public/hospital.html`, `public/js/api.js`, `public/js/triage.js`, `public/css/custom.css`.
- Backend: `app.py`, `database.py`, `triage_service.py`, `ttl_worker.py`.
- Tests: `tests/` directory (pytest backend API tests + E2E runner scripts).
