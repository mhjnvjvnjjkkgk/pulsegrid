# Forensic Audit Report — Milestone 3

**Work Product**: Milestone 3 Code Changes (`public/js/api.js`, `public/index.html`, `public/css/custom.css`, `app.py`)  
**Profile**: General Project (Integrity Mode: `development`)  
**Verdict**: CLEAN  

---

## 1. Observation

Direct empirical observations from source code inspection, static analysis, and test execution:

1. **OSRM Routing & Throttling (`public/js/api.js`, lines 325-360; `public/index.html`, lines 504-604)**:
   - `public/js/api.js` implements state-based OSRM route throttling helper `shouldFetchOSRMRoute(userLat, userLng, targetHospitalId, force, minIntervalMs=15000, minDistanceMeters=50)`.
   - `shouldFetchOSRMRoute` checks if `force` is true or if `_lastOSRMTargetId !== targetHospitalId`. Otherwise, it enforces both time interval (`timeElapsed >= 15000` ms) and distance threshold (`distMeters >= 50` m) before returning `true`.
   - `updateRouteToHospital(h, forceFetch)` in `public/index.html` calls `API.shouldFetchOSRMRoute`. When `!shouldFetch && routePolyline`, it skips redundant HTTP calls. When `shouldFetch` is true, it queries `https://router.project-osrm.org/route/v1/driving/...`, parses real GeoJSON geometry, distance, and duration, and updates UI metrics dynamically.
   - Fallback route logic uses Haversine formula with Kolkata street tortuosity factor (`1.42x`) and average speed (`18 km/h`) when offline or pending OSRM response.

2. **HTML5 `tel:` Links & Phone Binding (`public/index.html`, lines 173-176, 208-254, 526, 713, 1040-1067)**:
   - Quick-dial links use real emergency numbers: `tel:108` (National Emergency Response), `tel:102` (WB Health Emergency Hotline), `tel:1066` (Apollo Cardiac ICU Express), `tel:10501` (Fortis Mobile ICU Response).
   - Hospital cards dynamically bind phone links: `<a class="hosp-phone" href="tel:${h.emergency_phone || h.phone}">`.
   - Post-booking cockpit & drawer state dynamically set phone links to the reserved hospital's emergency phone: `callHospBtn.href = \`tel:${hospPhone}\``.

3. **UI Transformation & Cleanliness (`public/index.html`, lines 46-115, 1033-1102; `public/css/custom.css`)**:
   - `updatePostBookingUI(isActive)` transforms the drawer and cockpit UI when a hold is created: hides primary "Book Bed" button (`lockBtn.style.display = 'none'`), displays "Call Hospital" (`inline-call-hosp-btn`) and "Call Ambulance (108)" (`inline-call-amb-btn`) quick-dial action buttons, and displays OTP code, live countdown, and Google Maps turn-by-turn link. Reverts cleanly on cancellation.
   - Auto-scroll fix: `highlightCard(id, autoScroll = false)` in `public/index.html` line 843 sets `autoScroll` default to `false`. Background auto-refresh (`autoRouteNearest`) passes `false` to avoid background scrolling.
   - Demolition check: Zero occurrences of `judge-demo-bar`, `judge-demo-btn`, `runJudgeDemo`, `desk-btn`, or `Smart India Hackathon` badges in `public/index.html` and `public/css/custom.css`.

4. **Backend API & Test Bypass Audit (`app.py`, `database.py`, `tests/`)**:
   - `app.py` exposes REST endpoints (`/api/triage`, `/api/search`, `/api/facilities`, `/api/holds/create`, `/api/holds/redeem`, `/api/holds/cancel`, `/api/holds/location_update`, `/api/hospital/counter`, `/api/blood`).
   - No `TESTING` flag or test-bypass overrides exist in runtime application code (`app.py`, `database.py`, `triage_service.py`, `ttl_worker.py`, `public/js/api.js`).
   - `pytest` suite execution (`.\venv\Scripts\pytest.exe`): 37 passed in 0.90s across all test modules (`test_routing_postbooking.py`, `test_e2e_scenarios.py`, `test_gps_vector_api.py`, `test_holds_api.py`, `test_holds_engine.py`, `test_m1.py`, `test_triage_api.py`).

---

## 2. Logic Chain

1. **Observation 1** demonstrates that OSRM route recalculation is genuinely throttled using time (15s) and distance (50m) thresholds, eliminating jitter without hardcoded fake responses.
2. **Observation 2** confirms `tel:` links dynamically resolve target hospital emergency phone numbers from live data objects (`h.emergency_phone || h.phone`) or reference official regional emergency hotlines (108, 102, 1066, 10501).
3. **Observation 3** proves post-booking UI state transformation (`updatePostBookingUI`) is real, state-driven, and handles both activation and cancellation cleanly. The `autoScroll = false` parameter prevents background scrolling jumps, and all demo/judge UI artifacts are completely removed.
4. **Observation 4** confirms backend endpoints handle genuine database/in-memory operations without facade shortcuts or test bypasses. 100% of the test suite passes under independent execution.
5. **Conclusion**: Combining Steps 1-4, Milestone 3 code changes fully comply with requirement specifications and integrity guidelines.

---

## 3. Caveats

- Live OSRM HTTP lookup relies on third-party server (`router.project-osrm.org`). When offline or rate-limited by OSRM server, the frontend falls back to straight-line/Haversine route polyline, which is intended behavior.
- Web Speech API voice input requires browser support (`SpeechRecognition` / `webkitSpeechRecognition`), falling back to text input gracefully on unsupported browsers.

---

## 4. Conclusion

**Verdict: CLEAN**

Milestone 3 code changes (`public/js/api.js`, `public/index.html`, `public/css/custom.css`, `app.py`) are authentic, free of fake throttling, hardcoded tel links, facade UI elements, or test bypasses. All acceptance criteria for Milestone 3 are satisfied.

---

## 5. Verification Method

To independently verify this audit:

1. **Execute Automated Test Suite**:
   ```powershell
   .\venv\Scripts\pytest.exe
   ```
   *Expected result*: 37 passed in < 2 seconds.

2. **Inspect OSRM Throttling**:
   Inspect `public/js/api.js` lines 325-360 for `shouldFetchOSRMRoute` and `public/index.html` line 531.

3. **Inspect Post-Booking Quick-Dial Buttons**:
   Inspect `public/index.html` lines 172-179, 207-214, and 1033-1102 for `updatePostBookingUI`.

4. **Verify Removal of Demo/Judge Elements**:
   Confirm absence of `judge-demo-bar` or `desk-btn` in `public/index.html`.
