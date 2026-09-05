# 07 — FILE MAP AND OWNERSHIP

Every file has **exactly one owner**. Nobody edits somebody else's file without saying so out
loud — the Git history and the viva both depend on clean boundaries.

---

## 1. The complete tree

```
asha/
├── app.py                         M1   Flask app, all routes, CORS, startup
├── validators.py                  M1   input checking: phone, uuid, enums
├── database.py                    M2   the ONLY file that imports supabase
├── supabase_schema.sql            M2   tables, views, the 6 SQL functions
├── supabase_seed.sql              M2   12 Kolkata facilities + capacity + blood
├── triage_service.py              M3   classifier: keyword engine + optional LLM
├── triage_keywords.py             M3   the lexicon (English + Hindi/Hinglish)
├── ttl_worker.py                  M4   background thread, 10-second housekeeping
├── requirements.txt               M1
├── render.yaml                    M1   Render deployment config
├── vercel.json                    M1   Vercel static config for public/
├── .env.example                   M1
├── .gitignore                     M1
├── README.md                      M1
│
├── public/                             ← this folder is what Vercel serves
│   ├── index.html                 M6   citizen + paramedic screen
│   ├── hospital.html              M6   nurse desk screen
│   ├── css/
│   │   └── custom.css             M6   design tokens, glass recipes, keyframes
│   ├── js/
│   │   ├── config.js              M1   sets window.ASHA_API_BASE
│   │   ├── api.js                 M5   every fetch() in the project
│   │   ├── triage.js              M5   speech recognition + triage bar
│   │   ├── transit.js             M5   cockpit, countdown, OTP, cancel
│   │   ├── ui.js                  M5   renders cards, tiles, toasts
│   │   └── desk.js                M6   hospital desk behaviour
│   └── fonts/                     M6   self-hosted .woff2 files
│
├── tests/
│   ├── test_triage.py             M3   40 symptom phrases → expected severity
│   ├── test_ttl_expiry.py         M4   proves expiry works without the worker
│   └── test_holds_race.py         M4   proves two ambulances cannot share a bed
│
├── scripts/
│   ├── simulate_ambulance_rush.py M4   fires N concurrent holds — the demo showstopper
│   └── setup_git_history.sh       M1   the six-member branch/PR workflow
│
└── docs/                          M1   these 16 documents
```

## 2. Ownership table with size estimates

| Owner | Files | Est. lines | Their one-line pitch |
|---|---|---|---|
| **M1 — Lead** | `app.py`, `validators.py`, `requirements.txt`, `render.yaml`, `vercel.json`, `.env.example`, `.gitignore`, `public/js/config.js` | ~760 | "I built the API surface and the deployment: 13 endpoints, input validation, CORS, and the two-host setup." |
| **M2 — Database** | `database.py`, `supabase_schema.sql`, `supabase_seed.sql` | ~1040 | "I built the data layer and the PostgreSQL function that makes double-booking a bed mathematically impossible." |
| **M3 — Triage** | `triage_service.py`, `triage_keywords.py`, `tests/test_triage.py` | ~770 | "I built the classifier that turns 'seene mein dard' into RED · Cardiac ICU in six milliseconds, with or without internet." |
| **M4 — TTL / Time** | `ttl_worker.py`, `tests/test_ttl_expiry.py`, `tests/test_holds_race.py`, `scripts/simulate_ambulance_rush.py` | ~720 | "I own time in this system: reservations that release themselves, and the tests that prove three ambulances cannot take one bed." |
| **M5 — Client** | `public/js/api.js`, `triage.js`, `transit.js`, `ui.js` | ~990 | "I built everything the browser does: the live 4-second polling, Hindi voice input, and the countdown driven by server time." |
| **M6 — Design & Desk** | `public/index.html`, `public/hospital.html`, `public/css/custom.css`, `public/js/desk.js`, `public/fonts/` | ~1400 | "I built the Obsidian Vitals design system and the nurse's one-tap desk that a hospital can actually use at 3 a.m." |

Line counts are estimates and are **not** how contribution is judged. Commit count, PR
count and review comments are what GitHub Insights actually shows, and we distribute those
evenly — see [08-GIT-WORKFLOW](08-GIT-WORKFLOW.md).

## 3. Dependency order — who is blocked by whom

```
supabase_schema.sql  ─┐
supabase_seed.sql    ─┴─→ database.py ─┐
triage_keywords.py ─→ triage_service.py┤
                                        ├─→ app.py ─→ (running API)
                       ttl_worker.py ───┘                  │
                                                            ▼
04-API-CONTRACT.md ────────────────→ config.js → api.js → triage.js
       (frozen, so the frontend never waits)                 transit.js
                                                             ui.js
custom.css ─→ index.html / hospital.html ─→ desk.js
```

**The frozen API contract is what removes the blocking.** Members 5 and 6 build against
[04](04-API-CONTRACT.md) from hour one, using a small mock in `api.js` toggled by
`window.ASHA_MOCK = true`. They never sit idle waiting for the backend.

Practical build order for the lead:

1. `supabase_schema.sql` + `supabase_seed.sql` — run in Supabase, verify with §8 of [03](03-DATABASE-SCHEMA.md)
2. `database.py` — verify each function from a Python shell
3. `triage_keywords.py` + `triage_service.py` — runs with no database at all, so test it standalone
4. `validators.py`, then `app.py` — `curl` every endpoint against [04](04-API-CONTRACT.md)
5. `ttl_worker.py` — watch the console log tick
6. `custom.css` → `index.html` → `hospital.html`
7. `config.js`, `api.js`, `ui.js`, `triage.js`, `transit.js`, `desk.js`
8. `tests/` and `scripts/`
9. Deploy, then fill the viva dossier with real line numbers

## 4. Naming conventions

| Thing | Convention | Example |
|---|---|---|
| Python functions | `snake_case`, verb first | `create_live_hold`, `classify_symptoms` |
| Python constants | `UPPER_SNAKE` at module top | `CITIZEN_HOLD_MINUTES = 15` |
| SQL objects | `snake_case`; views prefixed `v_`; functions are verbs | `v_ward_availability`, `redeem_hold` |
| JS functions | `camelCase`, verb first | `renderFacilityCard`, `startCountdown` |
| JS module namespace | one global object per file | `window.AshaAPI`, `window.AshaUI` |
| DOM ids | `camelCase`, from the table in [06](06-SCREEN-SPECS.md) | `#facilityList` |
| CSS custom props | `--kebab-case`, grouped by prefix | `--vital-400`, `--dur-3` |
| CSS classes | `.block__element--modifier` for components, Tailwind for layout | `.ward-tile__count--critical` |
| Git branches | `feature/<area>-<short-desc>` | `feature/database-atomic-holds` |
| Commits | Conventional Commits | `feat(triage): add Hindi keyword lexicon` |

## 5. Two rules that prevent the most common wasted hours

1. **No file imports another member's file except through the documented function names.**
   `app.py` calls `database.get_facilities(...)`; it never reaches into Supabase itself.
2. **When something is unclear, the document changes before the code does.** A wrong
   assumption written down costs five minutes; the same assumption written into two files
   costs an evening.
