## 2026-09-05T18:36:58Z
You are worker_m1 for Milestone 1 (M1: Full-Screen Map UI & Unified Search).
Your working directory is d:\HACKATHON\.agents\teamwork_preview_worker_m1.
Project Plan: d:\HACKATHON\PROJECT.md
User requirements: d:\HACKATHON\ORIGINAL_REQUEST.md
Frontend Analysis: d:\HACKATHON\.agents\teamwork_preview_explorer_2\analysis.md
Backend Analysis: d:\HACKATHON\.agents\teamwork_preview_explorer_1\analysis.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

TASK: Implement Milestone 1 (R1 requirements):
1. **Full-Screen Map UI & Bottom Sheet**:
   - Restructure public/index.html & public/css/custom.css: 100% full-screen map background element (`#map`), floating top navbar containing search bar.
   - Restructure bottom sheet drawer matching native Google Maps UI (rounded top edges, drag handle, clean metrics, slidable up/down).
2. **Unified Search Bar & Bounds Fitting**:
   - Update public/js/triage.js, public/js/api.js, and backend app.py / triage_service.py:
   - Add blood group regex parser `/\b(O|A|B|AB)\s*([\+\-]|positive|negative)\b/i` to parse blood requests (e.g., "O- negative blood", "A+ blood needed") alongside medical symptoms.
   - Ensure backend supports blood group search without defaulting to General Ward.
   - Implement automatic map route fitting and bounds auto-zoom upon search submission.
3. **Voice Input Reliability**:
   - Fix voice recognition in public/index.html (line 1143 `bn-IN` tag): handle Benglish, Hinglish, and English voice input reliably without language misdetection errors.

Verify your changes, run tests, write changes.md, and send your handoff report when complete.
