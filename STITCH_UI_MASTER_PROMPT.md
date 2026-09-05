# STITCH MOBILE APP UI GENERATION PROMPTS (PULSEGRID EMERGENCY WEB APP)

This master prompt guide contains 3 detailed prompts to generate high-fidelity mobile app interfaces for **PulseGrid** in Google Stitch / Figma / Midjourney / DALL-E, strictly matching the user's hand-drawn sketches (**Drawings 1, 2, and 3**) with Apple Liquid Glassmorphism design system specifications.

---

## PROMPT 1: PHASE 1 — INITIAL BOOT SCREEN (DRAWING 1 ALIGNMENT)

```text
Design a hyper-realistic, ultra-premium mobile web application UI for an emergency hospital finder named 'PulseGrid', matching hand-drawn sketch Drawing 1 with Apple Liquid Glassmorphism aesthetic.

1. CANVAS & BACKGROUND:
- Mobile aspect ratio (19.5:9 notch display, iPhone 15 Pro container).
- Background: Full-screen Leaflet/Vector dark map of Kolkata (neutral dark tones, sleek cyan road veins, zero text watermarks).
- Ambient background glowing glass orbs (deep royal blue blur top-left, electric purple bottom-right, cyan glow bottom-center).

2. TOP NAVIGATION BAR (FLOATING GLASS HEADER):
- Positioned fixed top (16px inset from edges).
- Left: Round translucent glass button (44x44px) with 3 horizontal white hamburger lines.
- Right: Single round logo badge (44x44px) containing ONLY the letter 'P' in a glowing neon cyan circle with subtle pulse ring. NO text label beside it.

3. BOTTOM SEARCH CONTAINER (FLOATING GLASS CONTAINER):
- Floating at the bottom of the screen, 16px inset from left/right/bottom edges.
- Backdrop filter: Ultra-dense Apple Liquid Glassmorphism (blur 32px, saturate 200%, translucent gradient rgba(15, 23, 42, 0.88), border 1.5px solid rgba(255, 255, 255, 0.15), shadow 0 20px 50px rgba(0,0,0,0.6)).

- TOP BAR ABOVE SEARCH INPUT (7:3 RATIO MATRIX):
  - Spans 100% of the search bar width in a precise 7:3 grid ratio directly above the search box.
  - Left Item (70% Width): Translucent pill banner with text "Type blood group if required" in crisp white SF Pro font.
  - Right Item (30% Width): Glowing emerald green glass button with text "Nearest Hospital" in bold green font.

- MAIN SEARCH INPUT BOX:
  - Full-width pill input bar (height 56px, border-radius 999px).
  - Placeholder text: "Say YOUR SYMPTOM HERE..." in 50% opacity silver typography.
  - Right side icon: Circular glass microphone button 🎙️ glowing with subtle pulsing cyan voice ring.

4. DRAWER STATE:
- Zero drawer visible initially. 100% focus on full-screen map and bottom search bar.
```

---

## PROMPT 2: PHASE 2 — SEARCH TRANSITION & PEEK DRAWER STATE (DRAWING 2 ALIGNMENT)

```text
Design Phase 2 of the 'PulseGrid' emergency app UI after a user searches 'SEVERE CHEST PAIN', strictly matching hand-drawn sketch Drawing 2 with Apple Liquid Glassmorphism.

1. ANIMATED TOP SEARCH BAR:
- Search container has smoothly animated to the top navbar position (top: 16px).
- Search input filled with user text: "SEVERE CHEST PAIN" with glowing cyan border and small mic icon on right.
- Ambient backdrop darkens slightly with subtle map focus blur.

2. MAP ROUTE NAVIGATION CANVAS:
- Leaflet map shows blue animated driving route polyline connecting user's pulse location pin (blue dot with pulse rings) to destination hospital pin ('ILS Hospital, Nagerbazar').
- Map marker displays hospital pin with green glowing '+' badge and bed availability tag.

3. SLIDABLE BOTTOM SHEET DRAWER (PEEK PREVIEW STATE):
- Bottom sheet drawer has slid up from bottom covering bottom 40% of screen.
- Sheet styling: Apple Liquid Glassmorphism (radius top 28px, backdrop-filter blur 32px saturate 200%, translucent dark slate background, ambient top glass border).
- Top center: Rounded drag handle pill (width 40px, height 4px, silver translucent).

4. PEEK DRAWER CONTENT & 3 PRIMARY ACTION BUTTONS:
- Header Row: Hospital Title "ILS Hospital, Nagerbazar".
- Metrics Badges: Distance pill "[ 4 KM ]", Driving ETA pill "[ 15 Min ]", Open 24 Hours tag.
- Bed Availability Tag: Bold green text "🛏 4 Beds Available!".
- THREE PRIMARY ACTION BUTTONS (HORIZONTAL / GRID ROW):
  1. Button 1 (Primary Full-Width Accent): "🔒 Book MY Slot And Start" (glowing blue-green gradient button).
  2. Button 2 (Secondary Call): "🚑 Call Ambulance" (translucent red glass pill, href tel:108).
  3. Button 3 (Secondary Hospital Call): "📞 Call Hospital" (translucent cyan glass pill, href tel:emergency).
```

---

## PROMPT 3: PHASE 3 — EXPANDED DRAWER & DOCTOR-GRADE GUIDANCE (DRAWING 3 ALIGNMENT)

```text
Design Phase 3 of the 'PulseGrid' emergency app UI when the bottom sheet drawer is pulled up to full expanded state (85% screen height), strictly matching hand-drawn sketch Drawing 3 with Apple Liquid Glassmorphism.

1. TOP SEARCH BAR BEHAVIOR:
- Top search bar has smoothly animated offscreen top (hidden) to eliminate visual clutter and maximize reading room for medical emergency guidance.

2. FULL-HEIGHT SLIDABLE GLASS DRAWER:
- Sheet extends up to 85% viewport height.
- Smooth mobile scrollable container with custom invisible scrollbars.

3. DOCTOR-GRADE EMERGENCY PATIENT GUIDANCE CARD ("Things to Check and DO"):
- HEADER & ACUITY BADGE:
  - Title: "❤️ Severe Chest Pain / Heart Attack — Emergency Protocol"
  - Badge: "🚨 ESI-1 CRITICAL (Immediate Cardiac ICU Triage)" in red glowing glass pill.

- CLINICAL GUIDANCE SECTION CARDS:
  1. 🔍 CHECK IF PATIENT IS STRUGGLING:
     - Card with cyan left border: "Assess crushing chest pain radiating to left arm/jaw, cold sweating, dyspnea, nausea."
  2. ⚡ SOMETHING YOU CAN DO RIGHT NOW:
     - Card with green left border: "Sit patient upright at 45° angle (Semi-Fowler). Unbutton collar & loosen belt immediately."
  3. 📋 STEP-BY-STEP TACTICAL PROTOCOL (1-6 CHECKLIST):
     - Step 1: Chew one 300mg Soluble Aspirin (Disprin) if conscious and not allergic.
     - Step 2: Use sublingual Nitroglycerin spray/tablet under tongue if prescribed.
     - Step 3: Keep patient completely still; prohibit walking or physical exertion.
     - Step 4: Open windows for maximum room ventilation.
     - Step 5: Continuously monitor radial pulse rate and breathing.
     - Step 6: ER Resuscitation Bay & Cath Lab auto-notified with live GPS ETA.
  4. ⚠️ CRITICAL DO NOT DOs (RED WARNING BOX):
     - Crimson glass box: "❌ Do NOT lie patient flat (causes fluid backup in lungs). ❌ Do NOT allow walking or stairs. ❌ Do NOT give heavy food/drinks."
  5. 🧘 BYSTANDER CALMING SCRIPT (PURPLE SOOTHING BOX):
     - Purple glass box: "🗣️ Script for Bystanders: 'Breathe slowly: In through nose, out through mouth. Emergency cardiac bed is prepped.'"
  6. 🩸 LIVE BLOOD STOCK BREAKDOWN:
     - "🩸 Blood Stock Available: O-: 6u | O+: 18u | A+: 12u | B+: 24u | AB+: 10u"

4. BOTTOM ACTION FOOTER:
- Sticky glass footer at bottom of sheet with "🔒 Book MY Slot And Start", "🚑 Call Ambulance", "📞 Call Hospital".
```
