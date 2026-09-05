# Handoff Report — Backend Codebase Analysis

## 1. Observation
Direct evidence gathered from investigating the backend files in `d:\HACKATHON\`:

1. **Framework & Architecture**:
   - `requirements.txt` (lines 1-5): `flask>=3.0.0`, `flask-cors>=4.0.0`, `supabase>=2.0.0`, `python-dotenv>=1.0.0`, `gunicorn>=21.2.0`.
   - `app.py` (lines 25-37): Creates Flask server, calls `database.init_supabase()`, starts daemon thread `ttl_worker.start_ttl_worker(database)`.
   - `database.py` (lines 485-501): Dual-mode DB connection (Supabase PostgreSQL via `create_client` vs in-memory `MOCK_HOSPITALS` with 24 hospitals).

2. **Search & Triage Endpoints**:
   - `app.py` (line 60): `POST /api/triage` -> `triage_service.classify_symptoms(text)`.
   - `app.py` (line 76): `GET /api/facilities` -> `database.get_all_hospitals(specialty, ward)`.
   - `app.py` (line 183): `GET /api/blood` -> `database.get_blood_inventory(hospital_id)`.
   - `triage_service.py` (lines 14-391): `SYMPTOM_DATABASE` has ~400+ symptom keywords in English, Hinglish, Benglish, and Bengali script. Contains 0 blood group keyword entries (e.g., "O-", "O negative", "A+ blood needed").
   - There is NO `/api/search` or `/api/unified_search` endpoint in `app.py`.

3. **Soft-Lock & Hard-Lock Bed Reservation Engine**:
   - `app.py` (line 91): `POST /api/holds/create` -> `database.create_live_hold()`.
   - `app.py` (line 125): `POST /api/holds/redeem` -> `database.redeem_hold()`.
   - `database.py` (lines 635, 681): Expiry time hardcoded to 15 minutes (`minutes = 15`) for all hold types.
   - `database.py` (line 655): Mock mode returns `{"otp_code": otp_code, ...}`. Line 708: Supabase mode returns `{"otp": otp_code, ...}`.
   - `ttl_worker.py` (lines 9-16): Runs every 10 seconds calling `database.release_expired_holds()`.

4. **GPS Direction Vector Tracking & Movement Support**:
   - `app.py`: 0 routes exist for GPS location updates or movement tracking.
   - `supabase_schema.sql` (lines 68-80): `holds` table lacks columns for patient coordinates, speed, heading, movement status, or dynamic ETA.
   - `ttl_worker.py`: Has 0 logic for evaluating direction vectors or triggering wrong-direction auto-cancellations.

5. **Missing Endpoints**:
   - No `POST /api/holds/cancel` endpoint.
   - No `POST /api/holds/location_update` endpoint.
   - No `POST /api/search` (unified symptom + blood search) endpoint.

---

## 2. Logic Chain
- **Step 1 (Unified Search)**: Observation 2 shows that symptom triage (`/api/triage`), facility search (`/api/facilities`), and blood inventory (`/api/blood`) exist as 3 independent endpoints without blood group recognition in `triage_service.py`. Therefore, requirement R1 (unified search bar for symptoms + blood requirements like "O negative") cannot be serviced by a single backend API call.
- **Step 2 (Soft/Hard Lock Bugs)**: Observation 3 shows that `create_live_hold` returns `otp` in Supabase mode but `otp_code` in Mock mode. Furthermore, `minutes = 15` is hardcoded regardless of `hold_type`. Therefore, frontend integration faces schema mismatches between environments and cannot utilize 20-minute paramedic holds.
- **Step 3 (GPS & Movement Tracking)**: Observation 4 confirms that no API route, DB field, or worker logic exists for receiving or monitoring GPS coordinates. Therefore, requirement R2 (directional vector tracking, dynamic ETA vs stationary countdown, wrong direction auto-cancellation) has no backend persistence or execution support.
- **Step 4 (Hold Cancellation)**: Observation 5 shows no cancel endpoint exists. Therefore, holds abandoned by users remain locked for the full 15 minutes until TTL expiration.

---

## 3. Caveats
- Read-only investigation: No source code modifications were performed in `app.py`, `database.py`, `triage_service.py`, `ttl_worker.py`, or `supabase_schema.sql`.
- Client-side frontend implementations (e.g. `public/index.html` or `public/js/`) were not analyzed in this report as the task was specifically scoped to the backend codebase.

---

## 4. Conclusion
The PulseGrid backend is built on Flask + Supabase PostgreSQL with a robust 10-second TTL background worker and an extensive 400+ keyword triage engine. However, to fully satisfy user requirements R1, R2, and R3, the following backend additions/fixes are critical:
1. Implement a unified search endpoint `POST /api/search` handling both symptoms and blood group queries.
2. Standardize response payload key names in `create_live_hold` (`otp` vs `otp_code`) and respect `hold_type` duration (15m vs 20m).
3. Implement `POST /api/holds/location_update` endpoint and schema fields for GPS vector tracking, dynamic ETA, and movement-based wrong direction auto-cancellation.
4. Implement `POST /api/holds/cancel` for manual soft-lock release.

---

## 5. Verification Method
1. **File Inspection**:
   - Inspect `d:\HACKATHON\app.py` for route definitions.
   - Inspect `d:\HACKATHON\database.py` lines 616-717 for hold creation logic and key discrepancy (`otp` vs `otp_code`).
   - Inspect `d:\HACKATHON\triage_service.py` lines 14-391 to confirm lack of blood group keywords.
   - Inspect `d:\HACKATHON\supabase_schema.sql` lines 68-80 to verify `holds` table schema.
2. **Invalidation Conditions**:
   - If an existing route in `app.py` handles GPS tracking or unified search, this conclusion would be invalidated.
