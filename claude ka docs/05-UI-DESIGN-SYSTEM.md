# 05 — UI DESIGN SYSTEM: "OBSIDIAN VITALS"

**Owner:** Member 6. **File it becomes:** `public/css/custom.css` (tokens + recipes only;
layout stays in Tailwind classes).

---

## 1. The aesthetic decision, stated once

> **ASHA looks like the glass of an operating-theatre monitor at 3 a.m.**
> Deep obsidian, a slow teal aurora breathing behind frosted panels, and *one* colour —
> ember red — that is never used for decoration and only ever means *a human is in danger.*

This is a **dark, instrument-grade liquid glass** system. Two rules give it its character
and both are load-bearing:

1. **Colour has meaning or it is absent.** Teal is the system. Red is critical. Amber is
   urgent. Mint is available. Nothing is coloured because it looked nice. A judge who
   notices this will conclude the team thinks like clinicians.
2. **The interface has a pulse.** A live ECG trace runs under the header, and its rhythm
   tracks real system state — it quickens when a RED hold is active, and the aurora gains
   an ember bloom. **The background is a status display.** This is the one thing people
   remember about ASHA.

What we are explicitly *not* doing: purple-on-white gradients, floating 3D blobs, glass
over photographs, or anything that trades legibility for prettiness. In this product,
legibility *is* the aesthetic.

---

## 2. Typography

Three faces, each with a job. **Self-host all four** in `public/fonts/` as `.woff2` — venue
Wi-Fi must never be able to break our typography.

| Role | Face | Why this one |
|---|---|---|
| Display / headings | **Bricolage Grotesque** 600–800 | A grotesque with real character — slightly condensed, quirky terminals. Feels engineered, not templated. |
| Body / UI / labels | **Instrument Sans** 400–600 | Narrow, calm, excellent at small sizes. Stays out of the way. |
| **All numerals** | **Martian Mono** 400–700 | Every bed count, countdown, OTP and telemetry value. Genuinely tabular, so digits never jitter as they change. This is the font judges will stare at. |
| Hindi / Devanagari | **Noto Sans Devanagari** 400–700 | Multilingual triage input must render correctly. |

```html
<!-- Fallback CDN link. Ship self-hosted @font-face as the primary. -->
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;600;700;800&family=Instrument+Sans:wght@400;500;600;700&family=Martian+Mono:wght@400;500;700&family=Noto+Sans+Devanagari:wght@400;500;700&display=swap">
```

```css
--font-display: 'Bricolage Grotesque', 'Instrument Sans', system-ui, sans-serif;
--font-body:    'Instrument Sans', 'Noto Sans Devanagari', system-ui, sans-serif;
--font-mono:    'Martian Mono', ui-monospace, 'Cascadia Mono', monospace;
```

### Type scale

| Token | Size | Use |
|---|---|---|
| `--t-hero` | `clamp(2.25rem, 5vw, 3.5rem)` | Landing headline, Bricolage 800, `letter-spacing: -0.03em` |
| `--t-h1` | `clamp(1.75rem, 3.2vw, 2.25rem)` | Section titles, Bricolage 700, `-0.02em` |
| `--t-h2` | `1.375rem` | Card titles, Bricolage 600 |
| `--t-body` | `0.9375rem` | Everything, Instrument 400, `line-height: 1.6` |
| `--t-label` | `0.75rem` | Uppercase labels, Instrument 600, `letter-spacing: 0.09em` |
| `--t-micro` | `0.6875rem` | Timestamps, footnotes |
| `--t-num-xl` | `clamp(3rem, 9vw, 4.5rem)` | The OTP, the countdown. Martian 700, `-0.04em` |
| `--t-num-lg` | `2.5rem` | Ward tile bed counts. Martian 500 |
| `--t-num-sm` | `0.8125rem` | Inline counts, distances |

**Rule:** every element showing a number that changes gets
`font-variant-numeric: tabular-nums; font-family: var(--font-mono);`. A count that shifts
sideways when it changes from 9 to 10 looks broken, and on this product it looks *unsafe*.

---

## 3. Colour tokens

```css
:root {
  /* ── Obsidian base ─────────────────────────────────────────── */
  --ink-900:#05070B;  /* page                     */
  --ink-850:#080B12;
  --ink-800:#0B1018;  /* glass tint base          */
  --ink-700:#111826;  /* solid panel (hospital)   */
  --ink-600:#1A2333;  /* raised solid             */
  --ink-500:#253046;  /* borders, dividers        */

  /* ── Text ──────────────────────────────────────────────────── */
  --text-hi: #F2F6FB;  /* 17:1 on ink-900 — headings, numbers   */
  --text-mid:#A8B6C9;  /*  8:1 — body                            */
  --text-low:#6B7C93;  /*  4.6:1 — labels, ≥12px only            */
  --text-dim:#46556B;  /*  decorative rules only, NEVER text     */

  /* ── Vital teal: the system itself ─────────────────────────── */
  --vital-300:#7DF2E4;
  --vital-400:#3DE3D0;   /* primary accent, 11:1 on ink-900 */
  --vital-500:#1FC7B6;
  --vital-600:#12A79A;
  --vital-glow:rgba(61,227,208,.34);

  /* ── Triage semantics. Do not reuse decoratively. ──────────── */
  --crit-400:#FF5A6E;  --crit-500:#F0324B;  --crit-glow:rgba(255,90,110,.34);  /* RED    */
  --warn-400:#FFC24D;  --warn-500:#F5A623;  --warn-glow:rgba(255,194,77,.30);  /* YELLOW */
  --ok-400:  #4ADE9B;  --ok-500:  #22C57E;  --ok-glow:  rgba(74,222,155,.28);  /* GREEN  */
}
```

Every accent above clears **4.5:1 against `--ink-900`**, so accent-coloured text is legal
body text, not just decoration. Verified values: teal 11.2:1 · red 6.4:1 · amber 11.6:1 ·
mint 10.3:1.

### The colour contract

| Colour | Means exactly | Never used for |
|---|---|---|
| Teal | The system, its actions, its primary CTA | Any patient state |
| Ember red | RED triage · zero availability · destructive action | Emphasis, branding, headings |
| Amber | YELLOW triage · low availability (1–2) · stale data | Anything neutral |
| Mint | GREEN triage · healthy availability · success | Generic "on" states |

If a judge asks why the interface is so restrained with colour: *"In a triage product, red
has to mean one thing. If we spend it on a heading, we have spent the only colour a nurse
scans for."*

---

## 4. Geometry, spacing, elevation

```css
:root {
  --r-xs:6px; --r-sm:10px; --r-md:14px; --r-lg:20px; --r-xl:28px; --r-full:999px;

  /* 4-point scale */
  --s-1:4px; --s-2:8px;  --s-3:12px; --s-4:16px; --s-5:20px;
  --s-6:24px; --s-8:32px; --s-10:40px; --s-12:48px; --s-16:64px;

  --glass-blur:22px;
  --glass-alpha:.62;        /* hospital.html overrides this to .88 */
  --hairline:rgba(255,255,255,.14);
}
```

Only three elevation levels exist. More than three and depth stops reading as depth.

| Level | Used by | Shadow |
|---|---|---|
| 0 — flush | Page background, aurora | none |
| 1 — panel | Hospital cards, ward tiles, header | `0 1px 2px rgba(0,0,0,.4), 0 12px 32px -8px rgba(0,0,0,.55)` |
| 2 — overlay | Transit cockpit, modals, toasts | `0 2px 4px rgba(0,0,0,.5), 0 32px 80px -12px rgba(0,0,0,.75)` |

---

## 5. The glass recipe — copy this exactly

Four layers make glass read as *glass* rather than as a translucent rectangle: a **tint**, a
**blur**, a **top specular edge**, and a **hairline border that fades around the curve.**
Skip any one and it looks cheap.

```css
.glass {
  position: relative;
  border-radius: var(--r-lg);
  background:
    linear-gradient(180deg,
      rgba(255,255,255,.075) 0%,
      rgba(255,255,255,.022) 42%,
      rgba(255,255,255,.048) 100%),
    rgba(11,16,24,var(--glass-alpha));
  backdrop-filter: blur(var(--glass-blur)) saturate(155%);
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(155%);
  box-shadow:
    inset 0  1px 0 0 rgba(255,255,255,.14),   /* specular top edge  */
    inset 0 -1px 0 0 rgba(255,255,255,.035),  /* faint bottom bounce */
    0 1px 2px rgba(0,0,0,.4),
    0 12px 32px -8px rgba(0,0,0,.55);
}

/* Hairline border that brightens top-left and picks up teal bottom-right.
   Built with a masked pseudo-element because a plain 1px border cannot fade. */
.glass::before {
  content:''; position:absolute; inset:0; padding:1px;
  border-radius: inherit; pointer-events:none;
  background: linear-gradient(140deg,
    rgba(255,255,255,.30) 0%,
    rgba(255,255,255,.06) 34%,
    rgba(255,255,255,0)   58%,
    rgba(61,227,208,.18)  100%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
          mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
          mask-composite: exclude;
}

/* MANDATORY fallback. Older Android WebViews and Firefox-with-flags-off
   ignore backdrop-filter, and unblurred 62% glass over a moving aurora is
   unreadable. Go solid instead. */
@supports not (backdrop-filter: blur(2px)) {
  .glass { background: rgba(11,16,24,.94); }
}
```

### The cursor-tracked sheen (`.glass--live`)

Reserved for interactive glass — hospital cards, the primary CTA. Not every panel; a screen
where everything glints reads as noise.

```css
.glass--live::after {
  content:''; position:absolute; inset:0; border-radius:inherit;
  pointer-events:none; opacity:0; transition:opacity var(--dur-3) var(--ease-out);
  background: radial-gradient(220px circle at var(--mx,50%) var(--my,0%),
              rgba(255,255,255,.10), transparent 62%);
}
.glass--live:hover::after,
.glass--live:focus-within::after { opacity:1; }
```

Six lines of JS in `main.js` set `--mx` / `--my` from `pointermove`, throttled with
`requestAnimationFrame`, and skipped entirely when `(pointer: coarse)` matches — a finger
has no hover, so on phones this costs nothing.

### Density variant for the nursing station

```css
/* hospital.html sets this on <body>. Deliberate divergence, not inconsistency. */
body.desk { --glass-alpha:.90; --glass-blur:10px; }
```

**Rationale to give a judge:** a nurse reads this tile in under a second, from two metres
away, sometimes with gloved hands and a bright overhead light. Translucency costs contrast,
so on the hospital screen we spend less of it. The design system is the same; the density
token is tuned to the use case.

---

## 6. The living background — three fixed layers

Behind every glass panel, `z-index` −3 to −1, all `pointer-events: none`.

### Layer 1 — Aurora (`z:-3`)

Three blurred blobs drifting on long, unequal loops so the pattern never visibly repeats.

```css
.aurora { position:fixed; inset:-25%; z-index:-3; filter:blur(90px); opacity:.5; }
.aurora i { position:absolute; display:block; border-radius:50%; mix-blend-mode:screen;
            will-change:transform; }
.aurora .teal  { width:52vw; height:52vw; left:-6vw;  top:-4vw;
                 background:radial-gradient(circle,#1FC7B6 0%,transparent 68%);
                 animation:drift-a 38s ease-in-out infinite; }
.aurora .deep  { width:46vw; height:46vw; right:-8vw; top:22vh;
                 background:radial-gradient(circle,#1E48A8 0%,transparent 70%);
                 animation:drift-b 47s ease-in-out infinite; }
/* The ember. Opacity is driven from JS by live RED-hold count. */
.aurora .ember { width:40vw; height:40vw; left:26vw; bottom:-14vh;
                 background:radial-gradient(circle,#F0324B 0%,transparent 72%);
                 opacity:var(--ember,0); transition:opacity 1.6s ease;
                 animation:drift-c 31s ease-in-out infinite; }

@keyframes drift-a { 0%,100%{transform:translate3d(0,0,0) scale(1)}
                     50%    {transform:translate3d(7vw,5vh,0) scale(1.12)} }
@keyframes drift-b { 0%,100%{transform:translate3d(0,0,0) scale(1.06)}
                     50%    {transform:translate3d(-6vw,-7vh,0) scale(1)} }
@keyframes drift-c { 0%,100%{transform:translate3d(0,0,0) scale(1)}
                     50%    {transform:translate3d(4vw,-6vh,0) scale(1.18)} }
```

`--ember` is set to `min(0.10 + 0.10 * red_hold_count, 0.42)`. **The room gets warmer when
people are in danger.** Point this out on stage; it lands every time.

### Layer 2 — Grain (`z:-2`)

One fixed element for the entire page — never per-card.

```css
.grain { position:fixed; inset:0; z-index:-2; opacity:.038; pointer-events:none;
  mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.82' numOctaves='3'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)' opacity='.5'/%3E%3C/svg%3E");
}
```

Grain is what stops large dark areas from looking like flat digital emptiness. At 3.8% it is
invisible until you remove it.

### Layer 3 — Grid rule (`z:-1`)

A 64px hairline grid at 2.5% opacity, masked to fade out below 60% of the viewport height.
Reads as a calibrated instrument surface rather than a decorative pattern.

---

## 7. The signature element — the system pulse (ECG)

A 3px-tall SVG trace pinned under the header, full width. **This is the memorable detail.**

- One `<path>` with a real ECG waveform (baseline · P wave · QRS spike · T wave), stroked in
  `--vital-400` with a soft `drop-shadow` glow.
- Animated with `stroke-dasharray` / `stroke-dashoffset` so a bright pulse packet travels
  left to right.
- **The period is bound to system state:**

| State | Period | Stroke |
|---|---|---|
| Idle, nothing critical | `2.4s` | `--vital-400` |
| Any ACTIVE hold | `1.6s` | `--vital-300` |
| Any ACTIVE **RED** hold | `0.9s` | `--crit-400`, glow doubled |
| API unreachable | frozen flatline, `--text-dim` | + `OFFLINE` label |

A flatline when the backend dies is the correct, and slightly grim, joke. It also makes the
failure state unmissable, which is the real design goal.

Implementation: a single CSS custom property `--pulse-period` set from JS after each poll.
No JS animation loop; CSS does the work.

---

## 8. Motion

```css
:root {
  --dur-1:120ms;  /* tap / press feedback        */
  --dur-2:200ms;  /* hover, colour, small state  */
  --dur-3:320ms;  /* card enter, toast, list      */
  --dur-4:520ms;  /* cockpit takeover, modal      */
  --ease-out:   cubic-bezier(.16,1,.3,1);     /* expo-out: the "liquid" curve */
  --ease-spring:cubic-bezier(.34,1.56,.64,1); /* overshoot: OTP reveal only   */
  --ease-in-out:cubic-bezier(.65,0,.35,1);
}
```

Rules, in order of importance:

1. **Animate `transform` and `opacity` only.** Never `filter`, never `backdrop-filter`,
   never `width` / `height` / `top` / `left`. Animating blur is the single fastest way to
   drop a glass UI to 12 fps.
2. **One orchestrated entrance beats twenty scattered fidgets.** On load, the header, the
   triage bar, then the hospital cards reveal on a 60 ms stagger via
   `animation-delay: calc(var(--i) * 60ms)`, translating up 12px from `opacity:0`. Cap the
   stagger at 8 items; the ninth card onward appears immediately.
3. **Numbers roll, they do not jump.** When a bed count changes, the old digit slides up and
   out while the new one slides up and in (`--dur-2`), and the tile border flashes to
   `--vital-400` for 400 ms. The nurse must *notice* the change without watching for it.
4. **Nothing loops forever except the pulse and the aurora.** Perpetual motion inside
   content is fatiguing on a screen someone stares at for a 12-hour shift.
5. **Tap feedback is mandatory** on the `[+]` / `[-]` buttons: `scale(.94)` for `--dur-1`
   plus an expanding ring. Gloved fingers need confirmation the tap registered.

### `prefers-reduced-motion` — not optional

Vestibular disorders are common, and a jury member may have one.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration:.01ms !important; animation-iteration-count:1 !important;
    transition-duration:.01ms !important; scroll-behavior:auto !important;
  }
  .aurora i { animation:none; }          /* blobs hold still, gradient stays */
  .ecg-pulse { animation:none; }          /* static trace, still shows shape  */
  .glass--live::after { display:none; }   /* no sheen                         */
}
```

Everything must remain **fully usable and still attractive** with motion off: the countdown
falls back to plain numerals, the ECG becomes a static waveform, the aurora becomes a still
gradient. Nothing is only communicated by movement.

---

## 9. Component specs

### 9.1 Status pill

```
┌───────────────────────────┐
│ ● RED · CRITICAL          │   • 6px dot, currentColor, 2s soft pulse (RED only)
└───────────────────────────┘   • 11px Instrument 600, uppercase, .09em tracking
                                • bg color-mix(<accent> 14%, transparent)
                                • 1px border color-mix(<accent> 34%, transparent)
                                • radius --r-full, padding 4px 10px
```

**Always carries a word, never only a colour.** `RED · CRITICAL`, `YELLOW · URGENT`,
`GREEN · STABLE`. Roughly 1 in 12 men has a colour-vision deficiency; a red/green-only
severity system is unusable for them and, in a medical product, indefensible.

### 9.2 Availability badge

| `available_now` | Colour | Text |
|---|---|---|
| 0 | `--crit-400` | `FULL` |
| 1–2 | `--warn-400` | `2 LEFT` |
| 3+ | `--ok-400` | `5 AVAILABLE` |

Plus the freshness dot from `updated_seconds_ago`: mint under 120 s, amber under 600 s, grey
beyond, with a `title` / `aria-label` of `Updated 41 seconds ago`.

### 9.3 Hospital card

```
╭──────────────────────────────────────────────────────────╮
│ ● PRIVATE  CARDIAC CENTRE         ~4.2 km · ~13 min      │  labels row
│ R.N. Tagore Institute                                     │  Bricolage 600, 1.375rem
│ of Cardiac Sciences                                       │
│                                                            │
│  CARDIAC ICU        ADULT ICU                              │  --t-label, --text-low
│      2                  0                                  │  Martian 500, --t-num-lg
│  available          full                                   │
│  ─── 8 of 10 staffed ───   ─── 14 of 14 ───                │  thin progress rail
│                                                            │
│  🩸 O− PRBC 4u  TRAUMA READY   ·   B+ PLT 6u               │  blood chips
│                                                            │
│  ╭────────────────────────────────────────────────────╮   │
│  │   REQUEST LIVE TOKEN HOLD          15:00 TTL       │   │  teal CTA, full width
│  ╰────────────────────────────────────────────────────╯   │
│  ⟳ updated 41s ago                    2 beds held now      │  --t-micro
╰──────────────────────────────────────────────────────────╯
```

- `.glass .glass--live`, `--r-lg`, padding `--s-5`.
- Hover: `translateY(-3px)`, shadow to level 2, hairline gains teal. `--dur-2`.
- The **staffed rail** is the Ghost Bed made visible: a full-width track (`--ink-500`) with
  the staffed portion filled, and the unstaffed remainder shown as a **hatched** segment
  with the tooltip *"4 physical beds have no nurse assigned this shift."* No existing portal
  shows this, and it is the fastest way to explain the whole problem without speaking.
- `available_now = 0` → card drops to `opacity:.55`, CTA disabled, `FULL` pill in red.

### 9.4 Ward tile (hospital desk)

```
╭────────────────────────────────╮
│ ADULT ICU              ⌀ 4     │   ⌀ = ghost gap, amber if > 0
│                                 │
│    ╭─────╮   11 ╱ 14           │   Martian 700, --t-num-xl for the count
│    │  −  │   OCCUPIED           │   72×72px buttons, --r-md
│    ╰─────╯                      │
│    ╭─────╮   1 available        │   mint / amber / red by value
│    │  +  │   2 held             │
│    ╰─────╯                      │
╰────────────────────────────────╯
```

- Buttons **72×72 px minimum** — well past the 44 px accessibility floor, because this is
  operated fast, possibly with gloves.
- Press: `scale(.94)` + expanding ring, `--dur-1`. Optimistic update, then reconciled to the
  server's returned state. On error, the number snaps back **and** a toast explains why.
- Disabled `[−]` at 0 and `[+]` at `total_staffed`, both with a `title` explaining the limit
  rather than being silently dead.

### 9.5 Countdown ring

- 132 px SVG, two concentric circles: a track at `--ink-500` and a progress arc animated via
  `stroke-dashoffset`, `stroke-linecap: round`.
- Colour by time remaining: teal above 5 min → amber 5–2 min → red under 2 min, each with a
  matching `drop-shadow` glow.
- Centre: `MM:SS` in Martian 700 at `--t-num-xl`, tabular.
- Under 60 s: the whole ring gains a 1 s `scale(1.03)` breathing pulse.
- **Driven by `expires_at − server_time`**, corrected on every 1 s poll, never by counting
  local ticks. A phone with a wrong clock must not show a wrong countdown.
- `aria-live="polite"` announces only at **10, 5, 2, 1 minute and 30 seconds** — announcing
  every second would make a screen reader unusable.

### 9.6 The OTP display

The single most important number on the screen — it is what gets the patient through the gate.

```
      ╭────╮ ╭────╮ ╭────╮ ╭────╮
      │ 5  │ │ 8  │ │ 2  │ │ 1  │      each digit in its own glass cell
      ╰────╯ ╰────╯ ╰────╯ ╰────╯      Martian 700, --t-num-xl
        SHOW THIS CODE AT THE DESK       --t-label, --text-low, centred
              [ ⧉ Copy ]
```

- Digits reveal on a **90 ms stagger** with `--ease-spring` — a slight overshoot, so the code
  feels *issued* rather than merely printed. This is the emotional peak of the flow; it earns
  the one spring curve in the system.
- `letter-spacing: .12em`, cells 64×80 px.
- Copy button writes to clipboard and confirms inline. Also rendered as plain selectable text
  for anyone who cannot use the button.

### 9.7 Transit cockpit (the "modal")

Not a centred dialog. A **full-bleed takeover** that slides up from the bottom edge over a
backdrop-blurred page, deliberately breaking the card grid to signal *the situation has
changed*.

- Enter: `translateY(100%) → 0` plus `scale(.97) → 1`, `--dur-4`, `--ease-out`.
- Backdrop: `rgba(5,7,11,.72)` + `backdrop-filter: blur(8px)`.
- Asymmetric layout — countdown ring off-centre left at roughly 38% width, hospital details
  and the map bleeding off the right edge. Centred symmetry would read as calm; this screen
  should not read as calm.
- Contains: countdown ring · OTP cells · hospital name, ward and phone · `OPEN DIRECTIONS`
  (opens the device's own maps app) · `CALL HOSPITAL` (`tel:` link) · `CANCEL / REROUTE`
  (outlined red, requires a 2-second press-and-hold to prevent an accidental release).
- Focus is trapped inside; `Escape` prompts rather than closing, because a stray keypress must
  not silently drop a reservation.

### 9.8 Toast

Bottom-centre on mobile, bottom-right on desktop. Glass, level 2, `--r-md`, 4 px left accent
bar in the semantic colour. Slides in `translateY(16px) → 0` over `--dur-3`. Auto-dismiss at
5 s (7 s for errors), `aria-live="assertive"` for errors and `polite` otherwise. Maximum
three stacked; older ones collapse.

### 9.9 Skeletons

Never a spinner. Glass rectangles at the exact final dimensions with a 1.4 s diagonal shimmer
(`background-position` on a `linear-gradient`, not a `filter`). Layout must not shift when
real data lands — a jumping page in the first two seconds of a demo undoes a lot of polish.

### 9.10 Mode switcher (Citizen / Paramedic)

A segmented control in glass with a sliding teal indicator (`transform: translateX`,
`--dur-2`, `--ease-out`). Paramedic mode changes the accent to `--warn-400`, adds a
`108 DISPATCH` badge, and shows the 20-minute TTL — the interface visibly acknowledges a
different class of user with more authority.

### 9.11 Microphone button

- Idle: glass circle, teal mic glyph.
- Listening: two concentric rings expand and fade on a 1.4 s loop, and the glyph turns
  `--crit-400`. Live transcript appears in the input as interim text at `--text-low`, then
  commits to `--text-hi` when final.
- Unsupported browser: the button is **removed from the DOM entirely**, not disabled. A dead
  control is worse than an absent one.
- Always paired with a visible text input. Voice is an accelerator, never the only path.

---

## 10. Accessibility rules — the ones glass usually breaks

Glassmorphism fails accessibility in exactly four predictable ways. All four are handled.

| Failure | Our rule |
|---|---|
| Text over a moving gradient | **No text ever sits directly on the aurora.** All text is on a glass panel whose dark base is at least `--glass-alpha: .62`. Verify every text/background pair at 4.5:1 (3:1 for ≥24 px bold). |
| Invisible focus rings on glass | `:focus-visible` gets **two** rings: a 2 px `--vital-400` ring at 2 px offset, plus a 4 px `rgba(5,7,11,.9)` outer ring so it separates from any backdrop. Never `outline: none` without a replacement. |
| Colour-only meaning | Every severity and availability state carries an icon **and** a word. See 9.1. |
| Blur unsupported → unreadable | The `@supports not` block in §5 is mandatory, not a nicety. |

Also required:

- Semantic landmarks: `<header>`, `<main>`, `<nav>`, `<section aria-labelledby>`. One `<h1>` per page.
- Every icon-only button has an `aria-label`. The `[+]` button reads *"Admit one patient to Adult ICU"*, not *"plus"*.
- Live regions: `aria-live="polite"` on availability counts and the countdown milestones;
  `assertive` on hold-granted and hold-failed.
- Keyboard: full tab order, visible focus, `Enter` / `Space` on everything actionable,
  `Escape` closes toasts. The nurse desk must be fully operable with a keyboard because some
  hospital terminals have no touchscreen.
- Touch targets ≥ 44 px everywhere, ≥ 72 px on the ward counters.
- `<html lang="en">`, and any Hindi string wrapped in `<span lang="hi">` so screen readers
  switch pronunciation.
- Test at 200% browser zoom and at 320 px width. Both must work without horizontal scroll.

---

## 11. Performance budget

`backdrop-filter` is the most expensive property in mainstream CSS. It is also the whole look.
So we spend it deliberately.

| Rule | Number |
|---|---|
| Elements with `backdrop-filter` visible at once | **≤ 8** |
| Aurora blobs | exactly 3 |
| Grain layers | exactly 1, page-level |
| Properties animated | `transform`, `opacity` — nothing else |
| `will-change` declarations | only the 3 aurora blobs and the active cockpit |
| Target frame rate | 60 fps on a ₹15,000 Android phone |

Beyond the eighth glass element, cards use `.panel` — a solid `--ink-700` background with the
same hairline and radius. Visually near-identical in a dark UI, effectively free to render.
An `IntersectionObserver` promotes a card to real glass when it enters the viewport and demotes
it when it leaves.

**Test on a real mid-range Android phone before the demo, not just on a laptop.** Chrome
DevTools' 4× CPU throttle is the minimum bar; a physical device is the real one.

---

## 12. Copy tone

The words are part of the design.

| Do | Don't |
|---|---|
| `Bed held. Code 5821. Go now.` | `Success! Your booking has been confirmed 🎉` |
| `Taken 2 seconds ago. Next closest: Medica, 6.9 km.` | `Error: resource unavailable` |
| `4 physical beds have no nurse this shift.` | `Staffing discrepancy detected` |
| `Hold expired. Nobody arrived.` | `Session timeout` |
| `Server not responding. Showing data from 40 seconds ago.` | `Something went wrong!` |

Rules: short sentences. Present tense. Never an exclamation mark. Never an emoji in an error.
Every failure message names **what happened, when, and the next action.** Someone is reading
this in the worst hour of their life.

---

## 13. Build checklist for Member 6

- [ ] Fonts self-hosted in `public/fonts/`, `@font-face` with `font-display: swap`
- [ ] All tokens from §3, §4, §8 present in `custom.css` — zero hard-coded hex in HTML
- [ ] `.glass`, `.glass::before`, `.glass--live`, `@supports not` fallback, `.panel`
- [ ] Aurora (3 blobs) + grain + grid rule, all `pointer-events: none`
- [ ] ECG pulse with `--pulse-period` driven from JS
- [ ] `prefers-reduced-motion` block
- [ ] `:focus-visible` double ring
- [ ] Every component in §9 built and visually checked at 320 px, 768 px, 1440 px
- [ ] Contrast audit: every text/background pair recorded in a table with its ratio
- [ ] 60 fps confirmed on a physical Android phone
- [ ] `SIMULATED DATA · DEMONSTRATION ONLY` badge present and permanent on both pages
