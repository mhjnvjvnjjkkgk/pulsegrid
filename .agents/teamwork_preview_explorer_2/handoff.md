# Handoff Report — PulseGrid Frontend Architecture & Bug Analysis

**Agent:** `teamwork_preview_explorer_2`
**Target Work Directory:** `d:\HACKATHON\.agents\teamwork_preview_explorer_2`
**Date:** 2026-09-05T18:35:29Z

---

## 1. Observation

Direct observations from source code inspection of the PulseGrid frontend repository:

- **Observation 1.1 (Auto-Scroll Bug):** In `public/index.html`:
  - Line 745: `card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });` inside function `highlightCard(id)`.
  - Line 791: `highlightCard(match.hospital.id);` inside function `autoRouteNearest(wardKey)`.
  - Line 808: `autoRouteNearest('all');` inside function `loadHospitals()`.
  - Line 1191: `setInterval(loadHospitals, 60000);` periodically executes `loadHospitals()`.

- **Observation 1.2 (Map & Drawer UI Layout):** In `public/index.html`:
  - Lines 65–134: Hero section `<section class="hero fade-in">` is positioned above the map view.
  - Lines 139–213: `<div class="split-view">` contains `<div class="map-panel glass">` (left) and `<div class="cards-col" id="cards-col">` (right).
  - In `public/css/custom.css`:
    - Lines 413–426: `.map-panel` has `position: sticky; top: 80px; height: calc(100vh - 100px);`.
    - Lines 1105–1110: `@media (max-width: 768px) { .cards-col { max-height: 260px; overflow-y: auto; } }`.
    - There are no CSS rules or JS handlers for a slidable bottom sheet drawer with rounded top edges (`border-top-left-radius: 24px`) or touch drag handle.

- **Observation 1.3 (Unified Search Bar):** In `public/index.html`:
  - Lines 1073–1081:
    ```javascript
    document.getElementById('symptom-input').addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const val = e.target.value.trim();
      if (val.length >= 3) {
        debounceTimer = setTimeout(() => { runTriage(val); }, 300);
      }
    });
    ```
  - In `public/js/api.js` lines 258–267 (`runLocalTriage(text)`):
    Checks keywords `chest`, `heart`, `cardiac`, `stroke`, `seizure`, `bleeding`, `stomach`, `fever`, `vomiting`, `pain`, `asthma`, `breathe`. Does NOT contain regex or checks for blood groups (`O-`, `A+`, `B+`, `O+`, `blood needed`).

- **Observation 1.4 (Voice Recognition Language):** In `public/index.html`:
  - Line 1143: `recognition.lang = 'bn-IN';`.
  - In `public/js/triage.js` line 129: `recognition.lang = 'en-IN';`.

- **Observation 1.5 (Soft-Lock Bed Count Decrement):** In `public/index.html`:
  - Lines 908–930 (`createHold(h)`): Invokes `API.createHold(...)` and starts timer (`startCountdown(900)`), but does not mutate `allHospitals` array or re-render hospital cards to decrement visible count (e.g. 30 -> 29).

- **Observation 1.6 (GPS Tracking & Wrong Direction Logic):** In `public/index.html`:
  - Lines 383–410 (`initGPS()`): Updates `userLat`, `userLng`, calls `updateRouteToHospital(activeTargetHospital)`. If `curDist < lastDistanceToHospital - 0.03`, resets `remainingHoldSeconds = 900`.
  - Lines 461–499 (`updateRouteToHospital(h)`): Fires `fetch(osrmUrl)` on every single location update without rate limiting or minimum movement thresholding.
  - No logic tracking consecutive distance increases or triggering "Wrong Direction" alerts and auto-cancellation.

- **Observation 1.7 (Demo Elements):** In `public/index.html`:
  - Lines 46–56: `<a href="admin/" id="desk-btn" class="header-desk-btn">Hospital Desk →</a>`.
  - Lines 66–69: `<div class="hero-badge">Smart India Hackathon 2026 — SIH Team PulseGrid</div>`.
  - Lines 74–80: `<div class="judge-demo-bar delay-1">` with demo buttons for ESI-1, ESI-2, O- Blood.

- **Observation 1.8 (Post-Booking Cockpit Transformation):** In `public/index.html`:
  - Line 892: `if (cockpit) cockpit.style.display = 'none';` inside `openHoldModal()`. Hides the entire action cockpit.

---

## 2. Logic Chain

1. **Auto-Scroll Bug**:
   - Observation 1.1 shows that `loadHospitals()` calls `autoRouteNearest()`, which calls `highlightCard()`, which executes `card.scrollIntoView({ behavior: 'smooth', block: 'nearest' })`.
   - Because `loadHospitals()` runs periodically (every 60s or during polling/filter updates), `scrollIntoView()` fires automatically without user input, hijacking scroll position and scrolling the container to the nearest card.

2. **Map & Drawer Layout**:
   - Observation 1.2 shows that `.map-panel` is a fixed sticky container inside a two-column `.split-view` layout under a hero banner.
   - To achieve a 100% full-screen background map, `#map` must be positioned `fixed` across `100vw x 100vh`, top controls must float over `#map`, and hospital cards must be contained within a fixed bottom sheet drawer with rounded top edges and touch drag handles.

3. **Unified Search Engine**:
   - Observation 1.3 shows that `#symptom-input` passes all inputs directly to `runTriage()`, which only matches symptom terms.
   - Searching for "O negative" or "A+ blood" fails to match symptom terms, falling back to GREEN / General Ward without filtering blood inventory via `setBloodFilter()`.
   - Intercepting search input with a blood group regex prior to triage invocation will unify symptom and blood group search.

4. **Voice Input Misdetection**:
   - Observation 1.4 shows `recognition.lang = 'bn-IN'` in `index.html`.
   - Speaking Hinglish or English into a Web Speech instance set to `bn-IN` forces phonetic translation into Bengali Unicode script, corrupting input text.
   - Dynamic language switching or multilingual script normalization will eliminate transcription errors.

5. **Soft-Lock Bed Count Sync**:
   - Observation 1.5 shows `createHold` calls the backend but does not update `allHospitals` in memory.
   - Optimistically decrementing `available` by 1 and incrementing `held` by 1 immediately after `API.createHold` returns will update the visible count on screen instantly (e.g. 30 -> 29).

6. **GPS Tracking, ETA Jitter & Wrong Direction**:
   - Observation 1.6 shows `updateRouteToHospital()` fetches OSRM routes on every raw GPS event. GPS noise causes OSRM trip duration calculations to jump between 9 and 12 minutes.
   - Throttling OSRM API calls to 15s intervals and enforcing a >50m movement threshold will stabilize ETA displays.
   - Adding a distance delta checker with a `consecutiveWrongDirectionCount` counter will enable triggering a 30s confirmation modal and auto-canceling holds when users travel away from the target hospital.

7. **Post-Booking Action Cockpit**:
   - Observation 1.8 shows `openHoldModal()` sets `cockpit.style.display = 'none'`.
   - Transforming `#emergency-cockpit` to hide "Lock Bed" and present side-by-side quick-dial buttons (`tel:108` ambulance & `tel:<hospital_phone>`) satisfies requirement R3.

---

## 3. Caveats

- **Network Restrictions**: Investigation was conducted strictly within local filesystem scope (`CODE_ONLY` mode). External OSRM routing server latency and Web Speech API behavior were evaluated through code logic analysis.
- **Backend Hold API Schema**: `createHold` in `api.js` communicates with `/api/holds/create`. Backend database schema updates are handled by the backend explorer/implementer.
- No caveats regarding code inspection completeness — all relevant files in `public/` were fully read and analyzed.

---

## 4. Conclusion

The frontend codebase is well-structured but requires 8 targeted architectural adjustments to satisfy the full-screen Google Maps UI, unified symptom/blood search, stabilized GPS vector tracking, optimistic bed reservation soft-locking, post-booking quick-dial drawer, and background scroll stabilization requirements.

Detailed implementation specifications have been fully documented in `analysis.md`.

---

## 5. Verification Method

To independently verify all findings and line numbers:

1. **Verify Auto-Scroll Bug:**
   - Command: `grep -n "scrollIntoView" public/index.html`
   - Result: Line 745 in `highlightCard()`.
2. **Verify Voice Language Hardcoding:**
   - Command: `grep -n "recognition.lang" public/index.html public/js/triage.js`
   - Result: Line 1143 in `index.html` (`bn-IN`), Line 129 in `triage.js` (`en-IN`).
3. **Verify Demo Bar & Desk Link:**
   - Command: `grep -n "judge-demo-bar\|desk-btn" public/index.html`
   - Result: Lines 46-56 (`desk-btn`), Lines 74-80 (`judge-demo-bar`).
4. **Verify Cockpit Hiding:**
   - Command: `grep -n "emergency-cockpit" public/index.html`
   - Result: Line 218 (declaration), Line 892 (`display = 'none'`).
