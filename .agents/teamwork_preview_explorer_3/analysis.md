# Comprehensive Analysis: PulseGrid Testing Infrastructure, Environment Setup, and Verification Strategy

## Executive Summary

PulseGrid is a mobile emergency web app featuring an AI-driven symptom/blood search, Leaflet full-screen map, real-time soft-lock (15-min) and hard-lock (OTP redemption) hospital bed reservation engine, and dynamic ETA tracking.

This investigation evaluates the current Python environment, existing backend code, missing test suite infrastructure, offline database mock/fallback mechanics, and establishes a complete testing and verification strategy.

---

## 1. Python Environment & Backend Execution

### 1.1 Python Virtual Environment
- **Python Version**: `3.12.3` (Location: `d:\HACKATHON\venv\Scripts\python.exe`)
- **Virtual Environment Path**: `d:\HACKATHON\venv`
- **Activation Commands**:
  - Windows PowerShell: `.\venv\Scripts\Activate.ps1`
  - Command Prompt / Git Bash: `venv\Scripts\activate` or `source venv/Scripts/activate`

### 1.2 Installed Dependencies vs `requirements.txt`
`requirements.txt` contains:
```txt
flask>=3.0.0
flask-cors>=4.0.0
supabase>=2.0.0
python-dotenv>=1.0.0
gunicorn>=21.2.0
```

Installed package versions in `venv`:
- `Flask` (3.1.3)
- `flask-cors` (6.0.5)
- `supabase` (2.31.0)
- `python-dotenv` (1.2.3)
- `gunicorn` (26.2.0)

### 1.3 Key Finding — Missing Test Dependencies
`pytest`, `pytest-cov`, `requests`, `httpx`, and Playwright are **not** listed in `requirements.txt` nor installed in `venv`. To run automated tests, `pytest` must be added to project dependencies.

### 1.4 Backend Start Command
- **Development Server**: `venv\Scripts\python.exe app.py`
  - Runs Flask on `host="0.0.0.0"`, `port=5000` (or `PORT` environment variable).
  - Automatically initializes Supabase client (`database.init_supabase()`).
  - Starts background daemon thread for auto-expiring stale bed holds (`ttl_worker.start_ttl_worker(database)`).
- **Production Server (Linux/WSL)**: `gunicorn app:app --bind 0.0.0.0:5000 --workers 1`

---

## 2. Analysis of Existing Code vs Documented Test Plan

### 2.1 Codebase Audit Findings
- **Existing Test Files**: 0 test files exist in the repository (no `tests/` directory currently).
- **Existing Scripts**: 0 test scripts exist in the repository (no `scripts/simulate_ambulance_rush.py` currently).
- **Documentation Spec**: `claude ka docs/11-TEST-PLAN.md` specifies three planned automated test suites:
  1. `tests/test_triage.py`: Table-driven tests of 40 symptom phrases (English, Hinglish, Benglish, Bangla Unicode).
  2. `tests/test_ttl_expiry.py`: Proof of mathematical/view-based bed count recovery (`total - occupied - held`) when worker is dead.
  3. `tests/test_holds_race.py`: Double-booking concurrency prevention (8 simultaneous requests on 1 remaining bed).

---

## 3. Database Offline Mock / Fallback Architecture

### 3.1 Dual-Layer Fallback System
The application is designed to function 100% offline without external services (Supabase or external LLMs).

#### Layer 1: Backend Database Fallback (`database.py`)
- **Initialization**: `database.init_supabase()` checks `SUPABASE_URL` and `SUPABASE_KEY` from `.env`.
- If environment variables are omitted or invalid, or `supabase` package fails:
  - `supabase` global variable is set to `None`.
  - Server logs: `[DATABASE] NOTICE: SUPABASE_URL / KEY not set in .env. Running in Offline Mock Mode with 6 Kolkata hospitals.`
- **Mock Store**:
  - `MOCK_HOSPITALS`: Pre-populated array of 30 Kolkata hospitals with complete ward details (`adult_icu`, `pediatric_icu`, `cardiac_icu`, `general_ward`), specialties, and blood stock summaries (`A+`, `O-`, etc.).
  - `MOCK_HOLDS`: In-memory list tracking active reservations.
- **Operations**:
  - `get_all_hospitals()`: Filters `MOCK_HOSPITALS` by specialty or ward availability.
  - `create_live_hold()`: Generates random 4-digit OTP, appends to `MOCK_HOLDS`, increments ward `held` count by 1.
  - `redeem_hold()`: Validates OTP, updates status to `REDEEMED`, decrements `held` by 1, increments `occupied` by 1.
  - `release_expired_holds()`: Scans `MOCK_HOLDS`, marks expired holds (`expires_at < now()`), decrements `held` by 1.
  - `update_quick_counter()`: Increments/decrements `occupied` bed count.

#### Layer 2: Frontend API Client Fallback (`public/js/api.js`)
- `FALLBACK_HOSPITALS`: 30 full hospital objects embedded directly in frontend JS.
- `submitTriage()` & `fetchFacilities()` use a 4-second `AbortController` timeout. If the backend fails or times out, the frontend seamlessly executes local client-side triage (`runLocalTriage()`) and renders fallback hospitals.

---

## 4. Environment Variables Specification

### 4.1 `.env` Configuration Options
| Variable | Description | Recommended Local / Test Value |
|---|---|---|
| `SUPABASE_URL` | Supabase Project URL | `""` (empty for Mock Mode) |
| `SUPABASE_KEY` | Supabase Service Role Secret Key | `""` (empty for Mock Mode) |
| `PORT` | Flask HTTP Port | `5000` |
| `FLASK_ENV` | Environment mode | `development` or `testing` |
| `TTL_WORKER_ENABLED` | Toggle TTL background worker | `1` |
| `TTL_INTERVAL_SECONDS` | TTL poll interval in seconds | `10` |
| `TRIAGE_LLM_ENABLED` | Toggle LLM enhancement | `0` (Deterministic engine) |

---

## 5. Recommended Test & Verification Strategy

### 5.1 Suite 1: Backend API Unit & Integration Tests (`tests/test_api.py`)
Using `pytest` and Flask `app.app.test_client()`:
- `GET /`: Verify status 200 and version info.
- `POST /api/triage`: Test symptom classification (RED, YELLOW, GREEN) and ward recommendation.
- `GET /api/facilities`: Test listing and filtering by `specialty` and `ward`.
- `POST /api/holds/create`: Test 15-minute soft lock bed reservation & 4-digit OTP generation.
- `POST /api/holds/redeem`: Test OTP verification and bed admission (`held -> held-1`, `occupied -> occupied+1`).
- `POST /api/hospital/counter`: Test nurse quick counter updates (`+1`, `-1`).
- `GET /api/blood`: Test blood inventory queries.

### 5.2 Suite 2: Bed Locking & Concurrency Stress Tests (`tests/test_concurrency.py`)
- **Double Booking Race Condition**:
  - Spawn 8 parallel threads using `ThreadPoolExecutor`.
  - Issue 8 simultaneous `POST /api/holds/create` requests for 1 available bed.
  - Assert exactly 1 request returns HTTP 201 (`ACTIVE` hold with OTP) and 7 return HTTP 400 (`NO_CAPACITY`).
  - Assert available bed count never drops below 0.
- **TTL Soft-Lock Auto-Expiry**:
  - Create a hold, forcibly set `expires_at` into past.
  - Call `database.release_expired_holds()`.
  - Assert `status` transitions to `EXPIRED` and held bed count is restored.

### 5.3 Suite 3: Voice, Search & UI E2E Automation (`tests/test_ui_e2e.py`)
Using Playwright (`pytest-playwright`):
- **Full-Screen Map & Search**:
  - Verify map fills viewport, floating top navbar and bottom drawer render correctly.
  - Search symptom text (e.g. "severe chest pain" or Benglish "buke byatha") -> Verify map auto-zooms and bottom drawer updates with Cardiac ICU hospitals.
  - Search blood requirement (e.g. "O negative blood") -> Verify blood stock summary filtering.
- **Voice Input Simulation**:
  - Mock `window.SpeechRecognition` in browser context to emit voice recognition results (`saans nahi aa rahi`).
  - Verify automatic search submission and RED priority triage response.
- **Post-Booking Drawer UX (R3 Requirement)**:
  - Complete bed reservation -> Verify "Book Bed" button is replaced with "Call Ambulance" and "Call Hospital" quick-dial buttons.

---

## 6. Verification Commands & Execution Matrix

| Test Suite | Command | Objective |
|---|---|---|
| Environment Verification | `venv\Scripts\python.exe -c "import database, triage_service; print(database.get_all_hospitals()[:1])"` | Verify python environment and database mock initialization |
| API Test Execution | `venv\Scripts\python.exe -m pytest tests/test_api.py -v` | Validate all REST API endpoints using Flask test client |
| Concurrency Stress Test | `venv\Scripts\python.exe -m pytest tests/test_concurrency.py -v` | Validate thread safety against double-booking bed holds |
| Ambulance Rush CLI | `venv\Scripts\python.exe scripts/simulate_ambulance_rush.py` | Live CLI concurrency simulation |
