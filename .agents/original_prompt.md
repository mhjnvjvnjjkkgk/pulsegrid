## 2026-09-05T13:04:52Z

# Teamwork Project Prompt

Full-screen Google Maps style mobile emergency web app for PulseGrid with unified symptom/blood search, dynamic bottom drawer sheet, stabilized ETA calculation, and a real-time GPS soft-lock bed reservation system.

Working directory: d:\HACKATHON
Integrity mode: development

## Requirements

### R1. Full-Screen Google Maps Clone UI & Bottom Sheet
- Full-screen interactive map interface with floating top navbar and slidable bottom sheet drawer matching native Google Maps UI (rounded top edges, drag handle, clean metrics).
- Unified search bar supporting both medical symptoms (Hinglish/Benglish/English text or voice) and blood type requirements (e.g. "O negative", "A+ blood needed").
- Automatic map route fitting and bounds auto-zoom upon search submission.

### R2. Real-Time Soft-Lock & Hard-Lock Bed Reservation Engine
- 15-minute soft lock reserving 1 hospital bed immediately upon lock request.
- Live GPS tracking loop monitoring user directional vector and movement:
  - Moving toward hospital: Hides countdown timer, shows live dynamic ETA.
  - Stationary: Continues 15-minute countdown.
  - Moving away / ETA increasing 2-3 times: Triggers "Wrong Direction" alert; auto-cancels soft lock and restores bed count if unacknowledged.
- Hard lock: OTP verification at hospital entrance converts soft lock into permanent bed claim. Expiration without arrival restores bed to available pool.

### R3. Stabilized Routing, Polling & Post-Booking UX
- Fix ETA recalculation jitter/flickering (eliminating random 9-12 min jumps).
- Remove all judge/demo buttons, hospital desk navbar tabs, and random background auto-scrolling re-renders.
- Post-booking drawer transformation: Replace "Book Bed" button with single-tap "Call Ambulance" and "Call Hospital" quick-dial buttons.

## Acceptance Criteria

### UI & Map Interface
- [ ] Map renders 100% full-screen as background element with floating top search bar.
- [ ] Unified search bar handles both symptom text/voice and blood group requests (e.g., "O- negative blood").
- [ ] Benglish/Hinglish voice input works reliably without language misdetection errors.
- [ ] Bottom drawer slides smoothly up/down displaying exact beds, blood units, ETA, and distance.

### Soft-Lock & Bed Management
- [ ] Clicking "Lock Bed" reduces visible available beds by 1 (e.g. 30 -> 29) for 15 minutes and generates OTP.
- [ ] User movement towards target hospital pauses timer and displays live ETA.
- [ ] Moving away / wrong direction triggers warning prompt and auto-cancellation logic.
- [ ] Verification with OTP hard-locks the bed count at 29.

### Bug Fixes & Stability
- [ ] No auto-scrolling to bottom when hospital list refreshes in background.
- [ ] Judge Hackathon demo elements completely removed.
- [ ] Post-booking view shows only "Call Ambulance" and "Call Hospital" buttons.
