# PulseGrid Backend Architecture & Requirements Investigation Report

## Executive Summary
This report presents a thorough, read-only architectural investigation of the PulseGrid backend codebase (`app.py`, `database.py`, `triage_service.py`, `ttl_worker.py`, `supabase_schema.sql`, `requirements.txt`) evaluated against the requirements defined in `ORIGINAL_REQUEST.md` (R1, R2, R3).

---

## 1. Backend Architecture, Frameworks & Infrastructure

### 1.1 Technology Stack & Frameworks Used
- **Framework**: Flask (`flask>=3.0.0`) with `flask-cors>=4.0.0` for Cross-Origin Resource Sharing. Note: The backend uses **Flask (synchronous WSGI)**, NOT FastAPI or AsyncIO.
- **Environment & Deployment**: `python-dotenv>=1.0.0` for environment variables, `gunicorn>=21.2.0` as WSGI production server (`requirements.txt:1-5`).
- **Database Client**: `supabase>=2.0.0` client library for PostgreSQL communication (`requirements.txt:3`).

### 1.2 Application Entry Point & Initialization Flow
- **File**: `app.py`
- **Startup Sequence**:
  1. Loads `.env` environment variables via `load_dotenv()` (`app.py:23`).
  2. Instantiates Flask app `app = Flask(__name__)` and wraps with `CORS(app)` (`app.py:26-30`).
  3. Invokes `database.init_supabase()` (`app.py:33`).
  4. Launches background daemon thread `ttl_worker.start_ttl_worker(database)` (`app.py:36`).
  5. Listens on `host="0.0.0.0"`, `port=os.getenv("PORT", 5000)` (`app.py:194-198`).

### 1.3 Dual-Mode Database Architecture (Supabase PostgreSQL vs Offline In-Memory Mock)
- **File**: `database.py`
- **Supabase Integration**: Connects via `create_client(url, key)` (`database.py:496`).
- **Fallback Mock Engine**: If `SUPABASE_URL` / `SUPABASE_KEY` environment variables are absent or `supabase` module is not installed, `database.py` falls back to `MOCK_HOSPITALS` and `MOCK_HOLDS` (`database.py:485-501`).
- **Data Models & Schema (`supabase_schema.sql`)**:
  - `public.hospitals`: `id` (UUID), `name`, `address`, `latitude`, `longitude`, `phone`, `specialties` (TEXT[]), ward counts (`adult_icu_total/occupied/held`, `pediatric_icu_total/occupied/held`, `cardiac_icu_total/occupied/held`, `general_ward_total/occupied/held`), `updated_at` (`supabase_schema.sql:27-58`).
  - `public.holds`: `id` (UUID), `hospital_id` (UUID ref), `resource_type` (TEXT), `hold_type` (TEXT), `requester_phone` (TEXT), `otp_code` (TEXT), `status` ('ACTIVE', 'REDEEMED', 'EXPIRED'), `severity` ('RED', 'YELLOW', 'GREEN'), `created_at` (TIMESTAMPTZ), `expires_at` (TIMESTAMPTZ), `redeemed_at` (TIMESTAMPTZ) (`supabase_schema.sql:68-80`).
  - `public.blood_inventory`: `id` (UUID), `hospital_id` (UUID ref), `blood_group` (TEXT), `component` (TEXT: PRBC/Platelets/Plasma), `units_available` (INT), `units_reserved` (INT), `is_trauma_ready` (BOOL), `updated_at` (`supabase_schema.sql:97-106`).
- **Row Level Security (RLS)**: Explicitly disabled across all tables (`supabase_schema.sql:118-120`) because the backend uses the service key.

### 1.4 Background TTL Worker Mechanism
- **File**: `ttl_worker.py`
- **Implementation**: Spawns a daemon `threading.Thread` targetting `_worker_loop(db_module)` (`ttl_worker.py:18-24`).
- **Execution Loop**: Runs indefinitely with `time.sleep(10)` (`ttl_worker.py:9-16`). Every 10 seconds, it calls `database.release_expired_holds()`.
- **Expiration Logic**: Queries `holds` where `status == 'ACTIVE'` and `expires_at < NOW()`, updates status to `'EXPIRED'`, and decrements the corresponding `{resource_type}_held` count in `hospitals` (`database.py:777-828`).

---

## 2. Unified Search Endpoints (Symptom Triage + Blood Type Query)

### 2.1 Current Endpoint Implementations
1. **`POST /api/triage`** (`app.py:60`):
   - Accepts `{ "text": "<symptom description>" }`.
   - Calls `triage_service.classify_symptoms(text)` (`app.py:67`).
   - `triage_service.py` houses a static dictionary `SYMPTOM_DATABASE` (~400+ keyword rules) covering English, Hinglish, Benglish, and Bengali script (`triage_service.py:14-391`).
   - Returns `{ severity, recommended_ward, ward, explanation, reason, matched_keywords }` (`triage_service.py:446-453`).
2. **`GET /api/facilities`** (`app.py:76`):
   - Accepts query params `specialty` and `ward`.
   - Calls `database.get_all_hospitals(specialty, ward)`.
   - Formats available bed metrics per ward using `_format_hospital()` (`database.py:518-554`).
3. **`GET /api/blood`** (`app.py:183`):
   - Accepts optional query param `hospital_id`.
   - Calls `database.get_blood_inventory(hospital_id)` (`database.py:893-927`).

### 2.2 Critical Gaps in Search Architecture
- **MISSING UNIFIED SEARCH ENDPOINT**: Requirement R1 calls for a unified search bar handling both medical symptoms and blood group requirements (e.g. "O negative", "A+ blood needed"). The backend has NO unified endpoint (e.g. `POST /api/search` or `GET /api/search?q=...`) that parses a search string, identifies query intent (blood request vs medical symptom), and returns combined hospital bed & blood availability.
- **NO BLOOD KEYWORDS IN TRIAGE SERVICE**: `triage_service.py` contains zero entries for blood groups (e.g., `O-`, `O negative`, `A+`, `AB-`, `PRBC`, `Platelets`). Submitting "O negative blood needed" to `/api/triage` causes fallback to default `YELLOW` urgency and `general_ward` (`triage_service.py:435-444`).
- **NO BLOOD FILTERING ON FACILITIES ROUTE**: `GET /api/facilities` only filters by `specialty` and `ward`. It cannot filter hospitals by blood group availability.

---

## 3. Soft-Lock and Hard-Lock Bed Reservation Engine

### 3.1 Soft Lock Creation (`POST /api/holds/create`)
- **Endpoint**: `app.py:91-116`
- **Request Body**: `{ hospital_id, resource_type, hold_type, requester_phone/phone, severity }`.
- **Database Function**: `database.create_live_hold()` (`database.py:616-717`).
- **Logic**:
  1. Checks bed availability: `total - occupied - held > 0`. Returns 400 error if `available <= 0`.
  2. Generates random 4-digit OTP: `otp_code = str(random.randint(1000, 9999))`.
  3. Calculates expiry time: `expires_at = NOW() + timedelta(minutes=15)`.
  4. Inserts row into `holds` table with `status = 'ACTIVE'`.
  5. Increments `hospitals.{resource_type}_held` by 1.

### 3.2 Hard Lock Redemption (`POST /api/holds/redeem`)
- **Endpoint**: `app.py:125-135`
- **Request Body**: `{ hospital_id, otp_code }`.
- **Database Function**: `database.redeem_hold()` (`database.py:719-775`).
- **Logic**:
  1. Queries `holds` for active record with matching `hospital_id`, `otp_code`, and `status = 'ACTIVE'`.
  2. Updates hold status to `'REDEEMED'` and sets `redeemed_at = NOW()`.
  3. Decrements `hospitals.{resource_type}_held` by 1 and increments `hospitals.{resource_type}_occupied` by 1 (permanently claiming the bed).

### 3.3 TTL Worker Auto-Cancellation
- `ttl_worker.py` runs every 10s calling `database.release_expired_holds()`.
- Queries active holds where `expires_at < NOW()`.
- Updates hold status to `'EXPIRED'` and decrements `hospitals.{resource_type}_held` by 1.

### 3.4 Critical Soft/Hard Lock Bugs & Debt
- **JSON Key Mismatch Bug (`otp` vs `otp_code`)**:
  - In Supabase mode, `create_live_hold` returns `{"otp": otp_code, "hold_id": ...}` (`database.py:708`).
  - In Mock mode, `create_live_hold` returns `{"otp_code": otp_code, "hold_id": ...}` (`database.py:655`).
  - This break compatibility between online and offline modes.
- **Hardcoded 15-Minute Expiry (Ignores `hold_type`)**:
  - Schema documentation states `hold_type='citizen'` (15 min) and `hold_type='paramedic'` (20 min) (`supabase_schema.sql:72`).
  - However, `database.create_live_hold` hardcodes `minutes = 15` regardless of `hold_type` (`database.py:635,681`).
- **Non-Atomic Operations / Race Conditions**:
  - Checking availability and updating bed counts in `create_live_hold` are separate, non-atomic SELECT and UPDATE calls without database transaction locks or RPC stored procedures.
- **Missing Hold Cancellation Endpoint**:
  - No `POST /api/holds/cancel` or `DELETE /api/holds/<hold_id>` exists. Stale or abandoned user holds cannot be manually cancelled before 15 minutes expire.

---

## 4. GPS Direction Vector Tracking & Movement Monitoring API Support

### 4.1 Requirement R2 Specifications
- Real-time GPS tracking loop monitoring user directional vector and movement:
  - Moving toward hospital: Hides countdown timer, shows live dynamic ETA.
  - Stationary: Continues 15-minute countdown.
  - Moving away / ETA increasing 2-3 times: Triggers "Wrong Direction" alert; auto-cancels soft lock and restores bed count if unacknowledged.

### 4.2 Current Implementation Status
- **COMPLETELY MISSING IN BACKEND**:
  - **No API Endpoints**: Zero backend routes exist for receiving GPS coordinate updates, speed, heading, or directional vectors (e.g. `POST /api/holds/location_update`).
  - **No Database Persistence**: `public.holds` schema lacks columns for `user_latitude`, `user_longitude`, `speed`, `heading`, `distance_km`, `movement_status`, `eta_seconds`, or `wrong_direction_warnings`.
  - **No Movement Logic in Worker**: `ttl_worker.py` only checks fixed wall-clock time (`expires_at < NOW()`). It does not calculate dynamic ETAs, direction vectors, or wrong-direction auto-cancellations.

---

## 5. Summary Matrix of Technical Debt, Logic Bugs & Missing Endpoints

| Category | Requirement Ref | Issue Description | Location in Code | Severity |
|---|---|---|---|---|
| **Missing Endpoint** | R1 | No unified search endpoint (`/api/search`) to handle combined symptom triage & blood type queries | `app.py` | High |
| **Missing Endpoint** | R2 | No GPS location update / movement tracking endpoint (`/api/holds/location_update`) | `app.py`, `database.py` | High |
| **Missing Endpoint** | R2 | No manual hold cancellation endpoint (`POST /api/holds/cancel`) | `app.py`, `database.py` | High |
| **Missing Endpoint** | R1 | No blood reservation endpoint (`POST /api/blood/reserve`) | `app.py`, `database.py` | Medium |
| **Logic Bug** | R2 | Key mismatch in hold creation response: Supabase mode returns `otp`, Mock mode returns `otp_code` | `database.py:655,708` | High |
| **Logic Bug** | R2 | `hold_type` duration ignored; paramedic holds hardcoded to 15m instead of 20m | `database.py:635,681` | Medium |
| **Logic Bug / Debt** | R1 | `triage_service.py` has no blood group keyword rules; queries like "O negative" fall back to default General Ward | `triage_service.py:14-391` | High |
| **Technical Debt** | R2 | Non-atomic SELECT then UPDATE queries in hold creation/redemption (race condition risk) | `database.py:664-702` | Medium |
| **Technical Debt** | Architecture | Log message claims 6 hospitals in mock mode, but `MOCK_HOSPITALS` contains 24 and SQL seed data contains 12 | `database.py:486,493` vs `database.py:23-474` vs `supabase_schema.sql:127-215` | Low |

---

## 6. Proposed Fixes & Architectural Recommendations

1. **Implement Unified Search Endpoint (`POST /api/search`)**:
   - Create a single entry point in `app.py` that parses query strings for blood regex (`r'(A\|B\|AB\|O)[\s\-]*(positive\|negative\|\+\|-)'`) and symptoms, executing both triage classification and hospital blood/bed inventory filtering.
2. **Add GPS Tracking & Movement Persistence (`POST /api/holds/location_update`)**:
   - Add `user_lat`, `user_lng`, `heading`, `movement_status`, `eta_seconds` to `public.holds`.
   - Update `ttl_worker.py` to evaluate wrong direction / moving away status and trigger auto-cancellation when distance increases continuously.
3. **Standardize Hold Creation Response**:
   - Ensure both Supabase mode and Mock mode return identical keys: `{"otp": otp_code, "otp_code": otp_code, "hold_id": hold_id, ...}`.
4. **Implement `hold_type` Expiry Logic**:
   - Set `minutes = 20` when `hold_type == 'paramedic'` and `15` when `'citizen'`.
5. **Add Manual Hold Cancellation (`POST /api/holds/cancel`)**:
   - Allow frontend to explicitly release a soft lock when the user cancels or deviates route.
