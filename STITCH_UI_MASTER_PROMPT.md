# STITCH & V0 MASTER DESIGN PROMPT
## Full-Screen Emergency Hospital Bed & Blood Triage Logistics Engine (Google Maps Style)

Copy and paste the entire prompt below into **Stitch**, **v0**, **Claude Artifacts**, or any AI UI Generator to generate a clean, modern, production-grade interface for PulseGrid:

```markdown
# SYSTEM DIRECTIVE: GOOGLE MAPS CLONE EMERGENCY TRIAGE & BED RESERVATION MOBILE WEB APP

## 🎯 DESIGN PHILOSOPHY & AESTHETIC GUIDELINES
- **Theme**: Ultra-sleek, modern dark mode with Neobrutalistic Liquid Glassmorphism.
- **Color Tokens**:
  - Background Canvas: Dark Void `#060810` / Surface `#0d1526`
  - Accents: Neon Cyan `#38bdf8`, Royal Blue `#3b82f6`, Electric Purple `#8b5cf6`
  - Status Indicators: Emerald Green `#10b981` (Available Beds / Verified), Amber `#f59e0b` (Busy / Low Stock), Rose Red `#f43f5e` (Critical / Full / 108 Ambulance)
- **Typography**: `Outfit` (Headings, Titles, Badges, Metrics) & `Inter` (Body Text, Addresses, Inputs).
- **Layout Architecture**:
  - **100% Full-Screen Interactive Map Canvas** (`#map-container` taking `100vw` & `100vh`) as background.
  - **Floating Top Search & Location Cockpit** (`z-index: 1000`, fixed top, rounded pill containers with backdrop blur).
  - **Slidable Native Bottom Drawer Sheet** (`z-index: 1500`, 24px top rounded corners, drag handle, 3 snap states: Peek ~330px, Expanded 80vh, Collapsed 72px).

---

## 🛠 CORE UI COMPONENTS TO GENERATE

### 1. Floating Top Navigation & Search Cockpit
- **Header Pill**:
  - Left: Logo icon (`⚡` lightning pulse) + bold title **"PulseGrid"**.
  - Right: Live hospital counter badge (`🟢 40 Hospitals Live`).
- **Unified Search Bar**:
  - Pill-shaped container with search icon, text input (`"Describe symptoms or blood group… e.g., 'O- negative blood' or 'chhati me dard'"`), microphone icon for Web Speech Voice Triage (auto-detecting Hinglish, Benglish, English), and primary Search button.
- **Location Selector Quick Chips**:
  - Scrollable horizontal chip bar:
    - `[ 📍 Newtown (Amity) ]`
    - `[ 📍 Nagerbazar (Dum Dum) ]`
    - `[ 📍 Central Kolkata ]`
    - `[ 📡 Live GPS ]`
  - Clicking any chip re-centers the map, updates user location marker, and recalculates hospital distances/ETAs instantly.
- **Quick Symptom & Blood Chips**:
  - `[ 🫀 Chest/Heart ]` `[ 🩸 O- Blood ]` `[ 🩸 Trauma ]` `[ 🤰 Maternity ]` `[ 👶 Pediatric ]` `[ 🧠 Stroke ]`

---

### 2. Slidable Bottom Sheet Drawer (Google Maps Native UX)
- **Drag Handle Bar**: 52px rounded pill bar at top.
- **Sheet Header**:
  - Column title: **"Nearest Hospitals & Bed Availability"** + live count badge (`40 hospitals`).
  - Ward Filter Toolbar: `[ All Wards ]` `[ ❤️ Cardiac ICU ]` `[ 🏥 Adult ICU ]` `[ 👶 Pediatric ICU ]` `[ 🛏 General ]` `[ 🩸 O- Universal ]` `[ 🩸 A+ ]` `[ 🩸 B+ ]` `[ 🩸 O+ ]`.

---

### 3. Hospital Card Component Architecture (Zero Text Clipping & High Contrast)
Every card in the list must render:
- **Top Header Row**: Full hospital title (e.g., *SSKM Hospital (IPGMER)* or *Tata Medical Center*) wrapping naturally without truncation, accompanied by a subtle tag (`Govt` or `Private`).
- **Distance & ETA Subheader**: `📍 2.4 km • 🚗 8 mins` highlighted in cyan font (`#38bdf8`) + short address.
- **Prominent Staffed Bed Badge**: High-visibility green/amber banner pill:
  - `🛏 29 STAFFED BEDS AVAILABLE` + emergency phone link (`📞 033-6605-7000`).
- **Ward Capacity Bars**: Mini progress bars showing `Adult ICU`, `Cardiac ICU`, `Pediatric ICU`, and `General Ward` free bed counts and percentage capacity bars (`ok` green, `busy` amber, `full` red).
- **Blood Inventory Chips**: `🩸 O-: 8u` | `🩸 O+: 35u` | `🩸 A+: 20u` | `🩸 B+: 25u`.
- **Card Action Buttons**:
  - `[ 🔒 Lock Bed (15m) ]` — Primary vibrant gradient button with blue/purple glow.
  - `[ 🩸 Req Blood ]` — Rose red secondary action button.

---

### 4. Post-Booking UI State Transformation
When a user taps **"Lock Bed (15m)"**:
- Optimistically decrement visible beds (`30 -> 29`).
- Generate a 4-digit verification code (`8492`).
- Transform the bottom drawer into an active **Navigation & Emergency Dispatch Panel**:
  - Displays hospital name, address, 15-minute countdown timer (`15:00`), live GPS vector status badge (`📍 GPS Vector Active — Moving Toward Hospital`), and hold OTP code.
  - Quick-Dial Action Row:
    - **`[ 🚑 Call Ambulance (108) ]`** — Rose red primary quick dial.
    - **`[ 📞 Call Hospital ]`** — Cyan emergency desk dial.
    - **`[ 🗺 Open Turn-by-Turn in Google Maps ]`** — Direct navigation link.
    - **`[ ✕ Cancel Hold ]`** — Manual release button.

---

### 5. Interactive Map Features (Leaflet / Mapbox / OpenStreetMap)
- Custom map markers:
  - **Green Pin**: High bed availability ($\ge 10$ beds).
  - **Amber Pin**: Low bed availability ($< 10$ beds).
  - **Red Pin**: Full capacity ($0$ beds).
- **Blue Pulsing Beacon**: Live user GPS position marker with animated ring.
- **Cyan Route Polyline**: OSRM street-level driving route connecting user GPS to selected hospital with live turn-by-turn bounds zoom (`fitBounds`).
```
