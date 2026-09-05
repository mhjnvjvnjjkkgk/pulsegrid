## 2026-09-05T18:40:27Z
You are worker_m2 for Milestone 2 (Real-Time Soft/Hard-Lock Bed Reservation Engine).
Your working directory is d:\HACKATHON\.agents\teamwork_preview_worker_m2.
Project Plan: d:\HACKATHON\PROJECT.md
User requirements: d:\HACKATHON\ORIGINAL_REQUEST.md
Backend Analysis: d:\HACKATHON\.agents\teamwork_preview_explorer_1\analysis.md
Frontend Analysis: d:\HACKATHON\.agents\teamwork_preview_explorer_2\analysis.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

TASK: Implement Milestone 2 (R2 requirements):
1. **Soft-Lock Bed Reservation Backend & Frontend**:
   - 15-minute soft lock reserving 1 hospital bed immediately upon lock request.
   - Backend endpoints: `POST /api/holds/create` (ensure response key `otp_code` and bed_count), `POST /api/holds/redeem`, `POST /api/holds/cancel`, `POST /api/holds/location_update`.
   - Bed count decrement: On "Lock Bed" click, optimistically decrement visible available beds by 1 (e.g. 30 -> 29) for 15 minutes, generate 4-digit OTP, and show hold status panel.
   - Add manual release endpoint `/api/holds/cancel` so unacknowledged or canceled holds restore bed count (29 -> 30).
2. **Live GPS Tracking Vector Loop & Movement Monitoring**:
   - Implement user movement monitoring relative to target hospital (`POST /api/holds/location_update`).
   - Moving toward target hospital: Hide 15-minute countdown timer, display live dynamic ETA badge (e.g. `🚗 LIVE ETA: 11 mins`).
   - Stationary: Continue 15-minute countdown timer.
   - Moving away / ETA increasing 2-3 times: Trigger "Wrong Direction" alert prompt modal. Auto-cancel soft lock and restore bed count (29 -> 30) if unacknowledged or wrong direction continues.
3. **Hard Lock OTP Redemption**:
   - Hard lock: OTP verification at hospital entrance (`POST /api/holds/redeem`) converts soft lock into permanent bed claim, locking bed count at 29.
   - Expiration without arrival restores bed to available pool (29 -> 30).

Write unit/integration tests in tests/test_holds_engine.py, run `d:\HACKATHON\venv\Scripts\python.exe -m pytest d:\HACKATHON\tests`, write changes.md, and send handoff report when complete.
