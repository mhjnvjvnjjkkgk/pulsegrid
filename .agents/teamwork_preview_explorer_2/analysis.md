# Detailed Frontend Codebase Analysis — PulseGrid Citizen & Hospital Apps

**Target Directory:** `d:\HACKATHON\public`
**Analyzed Files:**
- `public/index.html` (1,196 lines)
- `public/hospital.html` (468 lines)
- `public/js/api.js` (284 lines)
- `public/js/triage.js` (589 lines)
- `public/css/custom.css` (1,266 lines)

---

## Executive Summary

This report presents an exhaustive, read-only architectural investigation of the PulseGrid frontend codebase across 8 specific focus areas requested by project requirements. 

Key architectural findings:
1. **Map Layout & Drawer Structure**: The current layout is a two-column desktop web view (`.split-view`) with a top hero section rather than a 100% full-screen background map with a native floating search bar and slidable bottom sheet drawer.
2. **Unified Search Engine**: Search handling (`#symptom-input`) passes all inputs to symptom triage (`runTriage()`) and lacks pattern matching to intercept blood group queries (e.g., "O- negative blood") and route them to `setBloodFilter()`.
3. **Voice Input Misdetection**: `index.html` hardcodes `recognition.lang = 'bn-IN'`, while `triage.js` hardcodes `recognition.lang = 'en-IN'`. Spoken English/Hinglish in `bn-IN` mode causes Bengali Unicode script mangling.
4. **Bed Soft-Lock UI & Counter Sync**: Locking a bed triggers `API.createHold()` backend creation, but the frontend in-memory state (`allHospitals`) does NOT optimistically decrement available bed count (30 -> 29) on screen until a network refresh occurs.
5. **GPS Tracking Loop & Routing**: Live tracking in `initGPS()` resets the hold timer to 15 minutes when moving forward rather than hiding the timer and displaying live ETA. "Wrong Direction" detection logic (2-3 consecutive distance increases) and auto-cancellation are completely missing. Unthrottled OSRM fetches on raw GPS updates cause ETA recalculation flickering.
6. **Hackathon / Judge Elements**: Judge quick demo buttons (`.judge-demo-bar`), hackathon hero title badge (`.hero-badge`), and top header `Hospital Desk →` button (`#desk-btn`) are present and need removal.
7. **Post-Booking Drawer Transformation**: Booking a bed currently hides the bottom cockpit bar (`#emergency-cockpit`) instead of transforming the drawer view to display side-by-side quick-dial "Call Ambulance" (108) and "Call Hospital" buttons.
8. **Auto-Scrolling Bug Root Cause**: `loadHospitals()` calls `autoRouteNearest()`, which calls `highlightCard()`, which calls `card.scrollIntoView({ behavior: 'smooth', block: 'nearest' })` on line 745 of `index.html`, hijacking user scroll position every time background polling occurs.

---

## Detailed Focus Area Analysis

### 1. Map UI Implementation & Layout Architecture

#### Current Codebase Inspection:
- **Files:** `public/index.html` (lines 139–213), `public/css/custom.css` (lines 398–430, 1105–1110).
- **DOM Hierarchy:**
  - `<section class="hero fade-in">` contains title, hackathon demo bar, quick chips, and `#symptom-input`.
  - `<div class="split-view">` contains two grid columns (`1fr 1fr` on desktop):
    - Left column: `<div class="map-panel glass">` containing `<div id="map"></div>` and `<div class="inline-reservation-panel">`.
    - Right column: `<div class="cards-col" id="cards-col">` containing scrollable hospital cards.
- **CSS Constraints:**
  - `.map-panel` has `position: sticky; top: 80px; height: calc(100vh - 100px);`.
  - On mobile screens (`@media (max-width: 768px)`), `.cards-col` is constrained to `max-height: 260px; overflow-y: auto;`.
  - `.emergency-cockpit` (lines 218–231 in `index.html`, 873–892 in `custom.css`) is a fixed bottom pill container (`position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);`).

#### Architectural Deficiencies:
- **Not Full-Screen Background Map**: The map is embedded within a standard page wrapper below the hero banner. It does not occupy `100vw x 100vh` as a base canvas.
- **No Native Slidable Bottom Sheet Drawer**: The cards column is a standard flex container. There is no swipe-draggable sheet UI with rounded top edges (`border-top-left-radius: 24px`, `border-top-right-radius: 24px`), top drag handle pill (`::before` / `<div class="drag-handle">`), and multi-state snapping (Collapsed peak ~120px, Half-screen ~50vh, Expanded ~90vh).

#### Proposed Code Changes:
- **`public/index.html` structure update:**
  ```html
  <!-- 100% Full-Screen Background Map Canvas -->
  <div id="map" style="position:fixed; inset:0; width:100vw; height:100vh; z-index:1;"></div>

  <!-- Floating Top Search Bar Overlay -->
  <div class="floating-top-bar" style="position:fixed; top:16px; left:50%; transform:translateX(-50%); width:92%; max-width:680px; z-index:1000;">
    <!-- Unified Search Bar & Chips -->
  </div>

  <!-- Slidable Bottom Sheet Drawer -->
  <div class="bottom-drawer-sheet" style="position:fixed; bottom:0; left:0; right:0; z-index:2000; border-radius:24px 24px 0 0;">
    <div class="drawer-drag-handle"></div>
    <div class="drawer-content">
      <!-- Hospital cards and metrics -->
    </div>
  </div>
  ```

---

### 2. Unified Search Bar (Symptoms & Blood Types)

#### Current Codebase Inspection:
- **Files:** `public/index.html` (lines 95–121, 1073–1089), `public/js/api.js` (lines 49–67, 258–267).
- **Current Search Flow:**
  - User typing in `#symptom-input` triggers 300ms debounced `input` listener:
    ```javascript
    document.getElementById('symptom-input').addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const val = e.target.value.trim();
      if (val.length >= 3) {
        debounceTimer = setTimeout(() => { runTriage(val); }, 300);
      }
    });
    ```
  - `runTriage(val)` passes text directly to `API.triage(val)`.
  - In `api.js`, `runLocalTriage(text)` checks for symptom keywords:
    - Critical (`chest`, `heart`, `cardiac`, `stroke`, `seizure`, `bleeding`) -> `RED` / `cardiac_icu`.
    - Acute (`stomach`, `fever`, `vomiting`, `pain`, `asthma`, `breathe`) -> `YELLOW` / `general_ward`.
    - Else -> `GREEN` / `general_ward`.

#### Deficiencies vs Requirement R1:
- Search bar does NOT inspect queries for blood types (e.g., "O negative", "O- negative blood", "need A+ blood", "B positive").
- If user types "O negative", `runLocalTriage` defaults to `GREEN` priority / `general_ward`! It fails to trigger `setBloodFilter('O-')` or filter hospital inventory.

#### Proposed Code Changes:
- Implement Unified Search Processor in `public/index.html` / `public/js/triage.js`:
  ```javascript
  function processUnifiedSearch(text) {
    const raw = (text || '').trim();
    if (!raw) return;

    // Blood type regex pattern matching
    const bloodRegex = /\b(O|A|B|AB)\s*([\+\-]|positive|negative)\b/i;
    const match = raw.match(bloodRegex);

    if (match) {
      const type = match[1].toUpperCase();
      const sign = match[2].toLowerCase();
      let normalizedGroup = type;
      if (sign === '+' || sign === 'positive') normalizedGroup += '+';
      else if (sign === '-' || sign === 'negative') normalizedGroup += '-';

      console.log(`[UnifiedSearch] Detected Blood Query: ${normalizedGroup}`);
      setBloodFilter(normalizedGroup);
      return;
    }

    // Default to Symptom Triage Engine if no blood group pattern detected
    runTriage(raw);
  }
  ```

---

### 3. Voice Input & Language Misdetection Issues

#### Current Codebase Inspection:
- **Files:** `public/index.html` (lines 1115–1185), `public/js/triage.js` (lines 114–192).
- **Code snippet from `index.html` line 1143:**
  ```javascript
  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = 'bn-IN'; // Hardcoded Bengali (India)
  ```
- **Code snippet from `triage.js` line 129:**
  ```javascript
  recognition.lang = 'en-IN'; // Hardcoded Indian English
  ```

#### Root Cause Analysis:
1. `index.html` hardcodes `recognition.lang = 'bn-IN'`. When a user speaks Hinglish or English (e.g. "severe chest pain"), Web Speech API forces phonetic transcription into Bengali script (`বাংলা`), creating gibberish output like `সিভিয়ার চেস্ট পেইন` or misrecognizing words completely.
2. Web Speech API `SpeechRecognition` object does not support automatic dual-language output switching on a single instance without dynamically changing `recognition.lang` or handling multilingual transcript normalisation.
3. `triage.js` contains a duplicate `initSpeechRecognition()` implementation that is unlinked in `index.html`.

#### Proposed Architectural Solution:
- Provide dynamic language toggle for voice mic (e.g. Default `hi-IN` / `en-IN` / `bn-IN` state) or normalize script:
  ```javascript
  let currentSpeechLang = 'bn-IN'; // Toggleable between 'bn-IN', 'hi-IN', 'en-IN'

  function toggleVoiceLang() {
    currentSpeechLang = currentSpeechLang === 'bn-IN' ? 'en-IN' : 'bn-IN';
    recognition.lang = currentSpeechLang;
    updateMicBadgeUI();
  }
  ```
- Map common Bengali Unicode terms (e.g. `বুক ব্যথা`, `ছাতি`, `পেট ব্যথা`, `রক্ত`, `শ্বাসকষ্ট`) in `runLocalTriage` keyword dictionary to ensure native script voice transcripts route correctly.

---

### 4. Soft-Lock UI Flow & Bed Reservation Engine

#### Current Codebase Inspection:
- **Files:** `public/index.html` (lines 873–952), `public/js/api.js` (lines 101–136).
- **Flow:**
  - User clicks "Hold Bed" (`openHoldModal(h)` line 879).
  - Calls `createHold(h)` -> `API.createHold(...)` (`api.js` line 101).
  - Backend creates hold and returns `otp_code` (e.g., `8492`).
  - Frontend displays `#inline-reservation-panel` with OTP code and starts 15-minute countdown (`startCountdown(900)` line 924).

#### Deficiencies vs Requirement R2:
- **Bed Count Decrement Bug**: When `API.createHold` succeeds, the frontend array `allHospitals` is NOT optimistically updated. The visible available bed count on the hospital card remains unchanged (e.g., 30) until an asynchronous backend poll refreshes the data.
- Spec requires: "Clicking 'Lock Bed' reduces visible available beds by 1 (e.g. 30 -> 29) for 15 minutes and generates OTP."

#### Proposed Code Changes:
- Add Optimistic UI Bed Count Decrement in `openHoldModal` / `createHold`:
  ```javascript
  async function createHold(h) {
    try {
      const result = await API.createHold(h.id, 'general_ward', 'citizen', '9999999999', 'YELLOW');
      
      // OPTIMISTIC UI DECREMENT
      const hosp = allHospitals.find(item => item.id === h.id);
      if (hosp && hosp.wards) {
        const targetWard = hosp.wards['General'] || Object.values(hosp.wards)[0];
        if (targetWard && targetWard.available > 0) {
          targetWard.available -= 1;
          targetWard.held += 1;
        }
      }
      renderCards(filterHospitals(allHospitals)); // Immediately update screen (e.g. 30 -> 29)
      
      startCountdown(900);
    } catch (err) { ... }
  }
  ```

---

### 5. GPS Tracking Loop Logic & ETA vs Countdown

#### Current Codebase Inspection:
- **Files:** `public/index.html` (lines 371–421, 426–515), `public/js/api.js` (lines 208–228).
- **GPS Watch Loop (`initGPS()` lines 383–410):**
  ```javascript
  navigator.geolocation.watchPosition((pos) => {
    userLat = pos.coords.latitude;
    userLng = pos.coords.longitude;
    if (activeTargetHospital) {
      updateRouteToHospital(activeTargetHospital);
      if (holdHospital && activeTargetHospital.id === holdHospital.id && remainingHoldSeconds > 0) {
        const curDist = API.calcDistance(userLat, userLng, holdHospital.latitude, holdHospital.longitude);
        if (lastDistanceToHospital !== null && curDist < lastDistanceToHospital - 0.03) {
          remainingHoldSeconds = 900; // Reset to 15 mins
          ...
        }
        lastDistanceToHospital = curDist;
      }
    }
  });
  ```

#### Detailed Bug Analysis:

1. **Jitter/Flickering in ETA Calculation (Fixing 9-12 min jumps)**:
   - `watchPosition` fires rapidly whenever GPS hardware reports position changes.
   - `updateRouteToHospital(h)` sends an HTTP GET request to `router.project-osrm.org` on every single position event (line 462).
   - GPS position drift (3–10 meter noise) causes OSRM duration responses to fluctuate wildly between e.g., 540s (9 mins) and 720s (12 mins).
   - *Fix:* Throttle OSRM API calls to once every 15 seconds, and apply an Exponential Moving Average (EMA) or minimum distance movement delta (e.g. > 50 meters) before recalculating route geometry.

2. **Movement Toward Hospital Logic**:
   - *Requirement:* "Moving toward hospital: Hides countdown timer, shows live dynamic ETA."
   - *Current Code:* `remainingHoldSeconds = 900` continuously resets the 15-minute countdown back to "15:00" and keeps the countdown timer visible, violating the requirement to hide countdown timer and show dynamic ETA when moving forward.

3. **Missing "Wrong Direction" Alert & Auto-Cancellation**:
   - *Requirement:* "Moving away / ETA increasing 2-3 times: Triggers 'Wrong Direction' alert; auto-cancels soft lock and restores bed count if unacknowledged."
   - *Current Code:* ZERO detection logic for user moving away from target hospital. No counter tracking distance increases, no alert modal, and no auto-cancellation hook to restore bed count (+1).

#### Proposed Architectural Solution:
```javascript
let consecutiveWrongDirectionCount = 0;
let lastDistanceToHospital = null;
let lastOSRMFetchTime = 0;

function handleGPSMovement(pos) {
  userLat = pos.coords.latitude;
  userLng = pos.coords.longitude;
  if (!activeTargetHospital) return;

  const curDist = API.calcDistance(userLat, userLng, activeTargetHospital.latitude, activeTargetHospital.longitude);
  
  if (lastDistanceToHospital !== null) {
    const delta = curDist - lastDistanceToHospital;

    if (delta < -0.03) {
      // 1. MOVING TOWARDS HOSPITAL
      consecutiveWrongDirectionCount = 0;
      // Hide countdown timer, show Live ETA badge
      document.getElementById('inline-timer-val').style.display = 'none';
      document.getElementById('live-eta-badge').style.display = 'inline-block';
      document.getElementById('live-eta-badge').textContent = `🚗 LIVE ETA: ${API.calcETA(curDist)}`;
    } else if (delta > 0.05) {
      // 2. MOVING AWAY FROM HOSPITAL
      consecutiveWrongDirectionCount++;
      if (consecutiveWrongDirectionCount >= 2) {
        triggerWrongDirectionAlert();
      }
    }
  }
  lastDistanceToHospital = curDist;
}

function triggerWrongDirectionAlert() {
  // Display prompt modal with 30s auto-cancellation warning
  showWrongDirectionModal({
    onAcknowledge: () => { consecutiveWrongDirectionCount = 0; },
    onTimeout: () => { cancelHoldAndRestoreBed(); }
  });
}
```

---

### 6. Judge Demo Buttons & Hackathon Elements Removal

#### Current Codebase Inspection:
- `public/index.html` lines 46–56: `<a href="admin/" id="desk-btn" class="header-desk-btn">Hospital Desk →</a>`.
- `public/index.html` lines 66–69: `<div class="hero-badge">Smart India Hackathon 2026 — SIH Team PulseGrid</div>`.
- `public/index.html` lines 74–80: `<div class="judge-demo-bar delay-1">` containing 3 demo buttons (`runJudgeDemo(1)`, `runJudgeDemo(2)`, `runJudgeDemo(3)`).
- `public/index.html` lines 1100–1112: `runJudgeDemo(scenarioId)` JavaScript function.
- `public/css/custom.css` lines 1151–1175: CSS rules for `.judge-demo-bar` and `.judge-demo-btn`.

#### Cleanup Specification:
1. Remove `.judge-demo-bar` DOM node from `index.html`.
2. Remove `runJudgeDemo()` JavaScript handler from `index.html`.
3. Remove `Hospital Desk →` link (`#desk-btn`) from sticky header in `index.html`.
4. Remove SIH hackathon references from `.hero-badge`.

---

### 7. Post-Booking Drawer Transformation

#### Current Codebase Inspection:
- `public/index.html` lines 218–231 (`#emergency-cockpit`), lines 891–893.
- In `openHoldModal()` (line 892):
  ```javascript
  const cockpit = document.getElementById('emergency-cockpit');
  if (cockpit) cockpit.style.display = 'none'; // Hides cockpit entirely!
  ```

#### Deficiencies vs Requirement R3 & Acceptance Criteria:
- Spec requires: "Post-booking drawer transformation: Replace 'Book Bed' button with single-tap 'Call Ambulance' and 'Call Hospital' quick-dial buttons."
- Spec requires: "Post-booking view shows only 'Call Ambulance' and 'Call Hospital' buttons."
- Hiding `#emergency-cockpit` leaves the user without quick-dial calling capabilities.

#### Proposed Architectural Solution:
- Instead of setting `cockpit.style.display = 'none'`, update `#emergency-cockpit` content:
  - Hide "🔒 LOCK ROUTE & RESERVE BED" button (`#cockpit-lock-btn`).
  - Render side-by-side equal-width action buttons:
    ```html
    <div class="post-booking-actions" style="display:flex; gap:10px; width:100%;">
      <a href="tel:108" class="btn-quick-dial amb-btn" style="flex:1; padding:14px; background:#f43f5e; color:#fff; border-radius:14px; text-align:center; font-weight:800; text-decoration:none;">
        🚑 Call Ambulance (108)
      </a>
      <a id="post-call-hosp-btn" href="tel:102" class="btn-quick-dial hosp-btn" style="flex:1; padding:14px; background:#38bdf8; color:#fff; border-radius:14px; text-align:center; font-weight:800; text-decoration:none;">
        📞 Call Hospital
      </a>
    </div>
    ```

---

### 8. Root Cause Analysis: Background Auto-Scrolling to Bottom

#### Code Traversal & Root Cause Chain:
1. In `public/index.html` line 1191: `setInterval(loadHospitals, 60000);` triggers periodic background updates.
2. `loadHospitals()` (lines 796–814) fetches facilities from API and invokes:
   ```javascript
   autoRouteNearest('all'); // Line 808
   ```
3. `autoRouteNearest(wardKey)` (lines 786–793) finds the nearest hospital matching the ward criteria and calls:
   ```javascript
   highlightCard(match.hospital.id); // Line 791
   ```
4. `highlightCard(id)` (lines 740–747) executes:
   ```javascript
   function highlightCard(id) {
     document.querySelectorAll('.hosp-card').forEach(c => c.classList.remove('highlighted'));
     const card = document.querySelector(`.hosp-card[data-id="${id}"]`);
     if (card) {
       card.classList.add('highlighted');
       card.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); // <-- CRITICAL BUG! Line 745
     }
   }
   ```

#### Consequence:
Every time `loadHospitals()` runs in the background (via interval timer or data poll), `highlightCard()` calls `card.scrollIntoView()`. This forcibly scrolls the card container / window down to position the nearest hospital card in view, forcibly overriding user manual scroll position and jumping to the bottom/middle of the page!

#### Fix Specification:
Update `highlightCard` signature and usage:
```javascript
// Add autoScroll parameter with default false
function highlightCard(id, autoScroll = false) {
  document.querySelectorAll('.hosp-card').forEach(c => c.classList.remove('highlighted'));
  const card = document.querySelector(`.hosp-card[data-id="${id}"]`);
  if (card) {
    card.classList.add('highlighted');
    if (autoScroll) {
      card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }
}

// In autoRouteNearest(wardKey):
highlightCard(match.hospital.id, false); // DO NOT scroll on background refresh

// On explicit map marker click event:
marker.on('click', () => {
  highlightCard(h.id, true); // Scroll ONLY on explicit user tap
});
```

---

## Verification & Independent Inspection Checklist

| Issue | File Location | Line Number | Independent Verification Method |
|---|---|---|---|
| Auto-scroll on refresh | `public/index.html` | Line 745 & Line 808 | Grep `scrollIntoView` in `index.html`. Confirm called inside `highlightCard()` invoked by `autoRouteNearest()` inside `loadHospitals()`. |
| Hardcoded Speech recognition `bn-IN` | `public/index.html` | Line 1143 | Inspect `initVoiceTriage()`. Confirm `recognition.lang = 'bn-IN'`. |
| Unhandled blood search in search input | `public/index.html` | Line 1073–1081 | Inspect `symptom-input` `input` event listener. Confirm `runTriage()` is called without blood regex parsing. |
| Missing optimistic bed count decrement | `public/index.html` | Line 908–930 | Inspect `createHold()`. Confirm `allHospitals` array is not updated before or after `API.createHold()`. |
| Hackathon Judge Bar & Header Button | `public/index.html` | Lines 46-56, 74-80 | View lines 46–80 in `index.html`. Confirm presence of `.judge-demo-bar` and `#desk-btn`. |
| Cockpit hidden post-booking | `public/index.html` | Line 892 | View `openHoldModal()`. Confirm `cockpit.style.display = 'none'`. |
