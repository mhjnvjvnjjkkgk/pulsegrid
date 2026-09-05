## 2026-09-05T18:43:09Z
You are worker_m3 for Milestone 3 (Stabilized Routing, Polling & Post-Booking UX).
Your working directory is d:\HACKATHON\.agents\teamwork_preview_worker_m3.
Project Plan: d:\HACKATHON\PROJECT.md
User requirements: d:\HACKATHON\ORIGINAL_REQUEST.md
Frontend Analysis: d:\HACKATHON\.agents\teamwork_preview_explorer_2\analysis.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

TASK: Implement Milestone 3 (R3 requirements):
1. **Fix ETA Recalculation Jitter/Flickering**:
   - Throttle OSRM routing fetches in public/index.html / public/js/api.js (e.g. 15s interval, >50m movement threshold) to eliminate random 9-12 min jumps in ETA display.
2. **Clean UI & Remove Demo/Judge Elements**:
   - Verify complete removal of all judge/demo buttons (`.judge-demo-bar`, `#desk-btn`), hospital desk navbar tabs, SIH hero badge text, and auto-scrolling on background hospital list refresh (`highlightCard` autoScroll flag).
3. **Post-Booking Drawer Transformation**:
   - When a bed hold is active (post-booking state), transform bottom sheet drawer UI:
   - Replace "Book Bed" button with single-tap quick-dial buttons: "Call Ambulance" (`tel:108`) and "Call Hospital" (`tel:<hospital_phone>`).
   - Hide redundant booking controls while hold is active.

Write tests in tests/test_routing_postbooking.py, run `d:\HACKATHON\venv\Scripts\python.exe -m pytest d:\HACKATHON\tests`, write changes.md, and send handoff report when complete.
