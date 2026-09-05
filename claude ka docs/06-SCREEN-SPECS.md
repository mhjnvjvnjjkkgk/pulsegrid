# 06 — SCREEN SPECS

**Owners:** Member 6 builds the markup and layout; Member 5 wires the behaviour. Read this
document together — every element below has an `id` that both members must agree on before
either starts.

Two pages only. No router, no SPA, no build step.

---

## 1. `public/index.html` — Citizen & Paramedic

### 1.1 Desktop layout (≥ 1024 px)

```
╔════════════════════════════════════════════════════════════════════════════╗
║  ⏻ ASHA               ● 12 HOSPITALS CONNECTED    ⌂ Hospital Desk →        ║  header (sticky, glass)
║  ∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿  ║  ECG pulse (3px)
║              SIMULATED DATA · DEMONSTRATION ONLY                           ║  honesty strip
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║        Every minute costs a life.                                          ║  hero, --t-hero
║        Stop driving hospital to hospital.                                   ║
║        ASHA reserves the bed before you move.                              ║  --text-mid
║                                                                            ║
║   ╭──────────────────────────────────────────────────────────────────╮    ║
║   │  ◉ CITIZEN          ○ PARAMEDIC · 108 DISPATCH                    │    ║  mode switcher
║   ╰──────────────────────────────────────────────────────────────────╯    ║
║                                                                            ║
║   ╭──────────────────────────────────────────────────────────────────╮    ║
║   │  🫀 CHEST / HEART   🩸 TRAUMA / BLEEDING   🤰 MATERNITY   🤕 OTHER │    ║  4 quick taps
║   │  ┌────────────────────────────────────────────────────┬────┬────┐│    ║
║   │  │ Describe what is happening…  (हिंदी भी चलेगा)      │ 🎤 │ →  ││    ║  triage bar
║   │  └────────────────────────────────────────────────────┴────┴────┘│    ║
║   ╰──────────────────────────────────────────────────────────────────╯    ║
║                                                                            ║
║   ╭─ TRIAGE RESULT ──────────────────────────────────────────────────╮    ║  appears after
║   │ ● RED · CRITICAL      ▸ CARDIAC ICU      chip: KEYWORD ENGINE     │    ║  classification
║   │ ████████████████████████████████░░░░  score 100                    │    ║  severity meter
║   │ Chest pain with breathing difficulty indicates a cardiac event.    │    ║
║   │ ⚠ Do not drive yourself. Call 108.                                 │    ║
║   ╰──────────────────────────────────────────────────────────────────╯    ║
║                                                                            ║
║   NEAREST FACILITIES WITH STAFFED CAPACITY          ⟳ live · every 4s      ║
║   ╭────────────────────╮ ╭────────────────────╮ ╭────────────────────╮   ║
║   │  hospital card     │ │  hospital card     │ │  hospital card     │   ║  3-col grid
║   ╰────────────────────╯ ╰────────────────────╯ ╰────────────────────╯   ║
╚════════════════════════════════════════════════════════════════════════════╝
```

### 1.2 Mobile (< 640 px)

Single column. Order changes deliberately:

1. Compact header (logo + connection dot only) with the ECG line
2. **Triage bar first** — the hero text collapses to one line, because on a phone the user is
   already in the emergency and does not need convincing
3. Quick-tap buttons as a 2×2 grid, each ≥ 64 px tall
4. Triage result
5. Hospital cards, full width, stacked
6. Sticky bottom bar once a hospital is selected: `REQUEST HOLD · 15 MIN`

### 1.3 Element IDs — the contract between Members 5 and 6

| `id` | Element | Member 5 does |
|---|---|---|
| `#connectionBadge` | Header status pill | Text + colour from `/api/health` |
| `#ecgPulse` | SVG trace | Sets `--pulse-period` and stroke class |
| `#modeCitizen` `#modeParamedic` | Mode radio inputs | Sets `state.holdType` |
| `#tapCardiac` `#tapTrauma` `#tapMaternity` `#tapGeneral` | Quick buttons | `POST /api/triage` with `category_tap` |
| `#triageInput` | Text input | Value source; also target for speech transcript |
| `#micButton` | Mic toggle | Speech recognition start/stop |
| `#triageSubmit` | Arrow button | `POST /api/triage` with `text` |
| `#triageResult` | Result panel | Unhides and fills |
| `#severityPill` `#severityMeter` `#wardChip` `#engineChip` `#triageExplain` `#triageAdvice` | Result fields | Fill from response |
| `#facilityList` | Card container | Renders cards, runs the 4 s poll |
| `#facilityCount` | "12 facilities" | Count from response |
| `#transitCockpit` | Full-bleed takeover | Show / hide, focus trap |
| `#countdownRing` `#countdownText` | Countdown | `expires_at − server_time` |
| `#otpCells` | 4 digit cells | Stagger reveal |
| `#cancelHold` | Press-and-hold button | `POST /api/holds/cancel` |
| `#toastStack` | Toast container | `showToast(kind, message)` |
| `#offlineBanner` | Stale-data banner | Shown after 2 consecutive failed polls |

**Rule:** Member 5 never invents an `id`, and Member 6 never renames one. If either needs a
change, this table changes first.

### 1.4 Every state that must be designed

| State | What the user sees |
|---|---|
| First load, before data | Skeleton cards (exact final size), ECG idle, `Locating facilities…` |
| Geolocation denied | Banner: `Location off — showing facilities by availability. Enable location for distance.` List still works. |
| Triage GREEN | Result panel in mint, **no hold button anywhere**, copy: `This does not need an emergency bed. Nearest clinic: …` |
| No facility has capacity | Full-width red panel: `No staffed ICU bed in 25 km. Call 108 — they can escalate to a government trauma centre.` plus the 3 nearest full hospitals shown greyed with their `held_now` counts |
| Hold succeeded | Cockpit takeover, OTP staggers in, ember rises in the aurora |
| Hold refused, `NO_CAPACITY` | Toast + card refreshes to `FULL` + the `alternatives` list scrolls into view. **The cockpit never opens.** |
| Hold refused, `DUPLICATE_HOLD` | Toast with a button: `You already hold a bed — open it` |
| Countdown under 2 min | Ring turns red and breathes; toast at 60 s: `2 minutes left. Confirm arrival at the desk.` |
| Hold redeemed by nurse | Cockpit flips to a mint full-screen: `ADMITTED. Bed confirmed.` Auto-closes after 6 s. |
| Hold expired | Cockpit flips amber: `Hold expired. Nobody arrived. Search again.` with a `SEARCH AGAIN` button |
| API unreachable | Flatline ECG, offline banner, last data kept on screen and dimmed with `Data from 40s ago` |

---

## 2. `public/hospital.html` — Hospital Desk

`<body class="desk">` — glass goes to 90% opacity and blur drops to 10 px. This screen is read
in one second from two metres away.

### 2.1 Layout (tablet landscape, 1024×768 — the target device)

```
╔════════════════════════════════════════════════════════════════════════════╗
║ ⏻ ASHA DESK   S.S.K.M. HOSPITAL ▾   ● ONLINE   14:32:07                   ║  header
║ ∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿  ║
╠════════════════════════════════════════════════════════════════════════════╣
║ ╭─ RAPID CHECK-IN ─────────────────────────────────────────────────────╮  ║
║ │   ┌────┐┌────┐┌────┐┌────┐                                            │  ║
║ │   │    ││    ││    ││    │      ╭───────────────────────────╮        │  ║  4 OTP boxes
║ │   └────┘└────┘└────┘└────┘      │   ✓  VERIFY & ADMIT       │        │  ║  + big green CTA
║ │   Type the patient's 4-digit code                            │        │  ║
║ ╰─────────────────────────────────────────────────────────────────────╯  ║
║                                                                            ║
║ WARD CAPACITY — TAP TO UPDATE                                              ║
║ ╭──────────╮ ╭──────────╮ ╭──────────╮ ╭──────────╮                       ║
║ │ADULT ICU │ │PEDIA ICU │ │CARDIAC   │ │GEN OXYGEN│                       ║  4 ward tiles
║ │ ⌀4       │ │ ⌀0       │ │ ⌀2       │ │ ⌀6       │                       ║
║ │  11/14   │ │   3/6    │ │   7/10   │ │  22/28   │                       ║
║ │ ╭──╮╭──╮ │ │ ╭──╮╭──╮ │ │ ╭──╮╭──╮ │ │ ╭──╮╭──╮ │                       ║
║ │ │− ││ +│ │ │ │− ││ +│ │ │ │− ││ +│ │ │ │− ││ +│ │                       ║  72×72 buttons
║ │ ╰──╯╰──╯ │ │ ╰──╯╰──╯ │ │ ╰──╯╰──╯ │ │ ╰──╯╰──╯ │                       ║
║ │ 1 free   │ │ 3 free   │ │ 2 free   │ │ 4 free   │                       ║
║ │ 2 held   │ │ 0 held   │ │ 1 held   │ │ 2 held   │                       ║
║ ╰──────────╯ ╰──────────╯ ╰──────────╯ ╰──────────╯                       ║
║                                                                            ║
║ LIVE INBOUND QUEUE                              3 patients en route         ║
║ ╭───────────────────────────────────────────────────────────────────────╮ ║
║ │ ● RED   5821   ADULT ICU    108 UNIT KA-01-AB-1234   ⏱ 08:32  [OVERRIDE]│ ║
║ │ ● RED   3390   CARDIAC ICU  Ramesh K · 98800•••45    ⏱ 04:11  [OVERRIDE]│ ║
║ │ ● AMBER 7104   GEN OXYGEN   Sunita D · 99001•••22    ⏱ 12:58  [OVERRIDE]│ ║
║ ╰───────────────────────────────────────────────────────────────────────╯ ║
║                                                                            ║
║ SHIFT HANDOVER — STAFFED BEDS            RECENTLY RESOLVED                 ║
║ ╭────────────────────────────╮  ╭──────────────────────────────────────╮  ║
║ │ Adult ICU     14  ─ ⊕      │  │ 3390 REDEEMED  Cardiac  14:30        │  ║
║ │ Cardiac ICU   10  ─ ⊕      │  │ 8812 EXPIRED   Adult    14:22        │  ║
║ ╰────────────────────────────╯  ╰──────────────────────────────────────╯  ║
╚════════════════════════════════════════════════════════════════════════════╝
```

### 2.2 Element IDs

| `id` | Purpose |
|---|---|
| `#hospitalSelect` | Which hospital this desk represents (persisted in `localStorage`) |
| `#otpBox1`–`#otpBox4` | Single-character inputs; auto-advance, auto-submit on the 4th |
| `#verifyAdmit` | Submits `POST /api/holds/redeem` |
| `#admitResult` | Full-width mint / red result banner |
| `#wardGrid` | Container for the four tiles |
| `#ward-adult_icu` … `#ward-general_oxygen` | One tile each |
| `#inboundQueue` | Live queue list |
| `#staffingPanel` | `total_staffed` adjusters |
| `#recentList` | Resolved holds |
| `#deskClock` | Server time, ticking |

### 2.3 Interaction rules

- **OTP boxes:** numeric keyboard on mobile (`inputmode="numeric"`), auto-advance on entry,
  backspace moves back, paste of `5821` fills all four, submit fires automatically on the
  fourth digit. A nurse should never have to reach for a button.
- **Success:** the banner fills the width in mint with the patient name, ward and severity at
  `--t-h1`, holds for 6 seconds, and the matching queue row slides out. A soft chime plays
  (respect `prefers-reduced-motion` by keeping the chime — it is not motion — but provide a
  mute toggle persisted in `localStorage`).
- **Failure:** boxes shake once (`translateX`, 240 ms), clear, and refocus box 1. The reason is
  spelled out: `Code 5821 expired 40 seconds ago.` — never just `Invalid`.
- **Queue timers** count down every second from `seconds_left` and `server_time`. Under 2
  minutes the row turns red and pulses.
- **`[OVERRIDE]`** is the paramedic escalation: admits the patient immediately even if the ward
  shows zero, on the grounds that a 108 crew at the door is a fact, not a request. It requires
  a confirm step and is logged. Explain it as *documented clinical override, not a bypass* — a
  system that cannot be overridden by a human at the bedside will be abandoned by staff.
- **Polling:** 4 s for the dashboard, 1 s locally for the queue countdowns.
- **No login.** Stated plainly in the docs and the viva as a deliberate prototype gap; the
  real deployment binds a desk to a device certificate.

### 2.4 States

| State | Screen |
|---|---|
| Loading | Skeleton tiles + `Connecting to ASHA…` |
| Empty queue | Centred, calm: `No inbound patients. All quiet.` in `--text-low` |
| Ward at zero available | Tile border turns red, count in red, `[+]` disabled with a tooltip |
| Ghost gap > 0 | Amber `⌀ 4` chip top-right; tap opens `4 beds here have no nurse this shift` |
| API down | Header dot red, flatline ECG, tiles frozen and dimmed, banner `Reconnecting…`, taps queued and replayed on reconnect |

---

## 3. Shared header

Identical structure on both pages so they read as one product:

1. Logo mark — a stylised ECG spike forming an `A`, teal, 28 px. The QRS peak *is* the
   apex of the letter; the baseline before and after it is the crossbar.
2. Wordmark `ASHA` in Bricolage 800, `letter-spacing: -.02em`, with `आशा` set beside it in
   Noto Sans Devanagari at 0.62× the wordmark size, `--text-mid`. The Devanagari is not
   decoration — the name means *hope*, and half our users read that word before the Latin one.
   *(Devanagari, not Bengali `আশা`, because Noto Sans Devanagari is already loaded for Hindi
   triage input and Bengali would be a second font file for two glyphs. If the venue turns out
   to be a Bengali-first room, swapping it is one `<link>` and one `font-family` — M6's call,
   made once, before the fonts are self-hosted.)*
3. Connection badge — dot + `12 HOSPITALS CONNECTED` / `RECONNECTING…` / `OFFLINE`
4. Cross-link to the other page
5. Server clock in Martian Mono, HH:MM:SS, ticking
6. ECG pulse line beneath, full width
7. The `SIMULATED DATA · DEMONSTRATION ONLY` strip

Height: 64 px desktop, 56 px mobile. Sticky, glass, `z-index: 40`.

---

## 4. What we are NOT building on these screens

Say this if asked, rather than being caught with a dead button: no admin panel, no login
screen, no historical charts, no district-level map view, no notification centre, no settings
page. Two screens, both fully functional, is a stronger prototype than six screens where four
are mockups. **There must be no non-functional button anywhere in the build.**
